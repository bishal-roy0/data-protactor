"""Run the versioned synthetic Karna baseline evaluation and emit transparent metrics."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient

from sentinel_ai.main import app

DATASET_PATH = Path("tests/fixtures/evaluation_cases_v1.json")
OUTPUT_PATH = Path("docs/evidence/evaluation_metrics_v1.json")
EVALUATED_CATEGORIES = (
    "safe",
    "phishing",
    "social_engineering",
    "impersonation",
    "scam",
    "suspicious_url",
    "malware_download",
)


def calculate_metrics(expected: list[str], actual: list[str], category: str) -> dict[str, float | int]:
    pairs = list(zip(expected, actual, strict=True))
    true_positive = sum(want == category and got == category for want, got in pairs)
    false_positive = sum(want != category and got == category for want, got in pairs)
    true_negative = sum(want != category and got != category for want, got in pairs)
    false_negative = sum(want == category and got != category for want, got in pairs)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    false_positive_rate = false_positive / (false_positive + true_negative) if false_positive + true_negative else 0.0
    return {
        "tp": true_positive,
        "fp": false_positive,
        "tn": true_negative,
        "fn": false_negative,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "false_positive_rate": round(false_positive_rate, 3),
        "sample_size": len(pairs),
    }


def main() -> None:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    client = TestClient(app)
    evaluated_cases = [case for case in dataset if case["modality"] in {"text", "url"}]
    results = []
    for case in evaluated_cases:
        response = client.post("/analyze", json=case["payload"])
        response.raise_for_status()
        results.append(
            {
                "id": case["id"],
                "expected_category": case["expected_category"],
                "actual_category": response.json()["threat_category"],
                "actual_action": response.json()["recommended_action"],
            }
        )

    expected = [item["expected_category"] for item in results]
    actual = [item["actual_category"] for item in results]
    report = {
        "dataset_version": "v1",
        "evaluated_samples": len(results),
        "non_evaluable_image_samples": len(dataset) - len(results),
        "exact_category_matches": sum(want == got for want, got in zip(expected, actual, strict=True)),
        "confusion_counts": Counter(f"{want}->{got}" for want, got in zip(expected, actual, strict=True)),
        "metrics_by_category": {
            category: calculate_metrics(expected, actual, category)
            for category in EVALUATED_CATEGORIES
        },
        "case_results": results,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
