"""Regression scenarios for Karna's explainable baseline rules.

These synthetic cases confirm expected rule behavior. They are not a claim of
real-world malware-detection accuracy or a substitute for a labeled benchmark.
"""

import pytest
from fastapi.testclient import TestClient

from sentinel_ai.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    ("payload", "category", "action"),
    [
        ({"text": "See you at the team meeting tomorrow."}, "safe", "allow"),
        ({"urls": ["https://example.com/help"]}, "safe", "allow"),
        (
            {"text": "Urgent: verify your account now with your OTP."},
            "phishing",
            "quarantine",
        ),
        (
            {"text": "Please buy a gift card immediately and send the code."},
            "social_engineering",
            "block",
        ),
        (
            {"text": "I am your boss. Please arrange a wire transfer immediately."},
            "impersonation",
            "quarantine",
        ),
        ({"urls": ["https://xn--e1afmkfd.xn--p1ai/login"]}, "suspicious_url", "show_caution"),
        ({"urls": ["https://192.0.2.12/login"]}, "suspicious_url", "show_caution"),
        (
            {"urls": ["https://example.com/continue?redirect=https://other.example"]},
            "suspicious_url",
            "show_caution",
        ),
        (
            {"urls": ["https://example.com/private-video"]},
            "suspicious_url",
            "show_caution",
        ),
        ({"urls": ["https://example.com/update.exe"]}, "malware_download", "block"),
    ],
)
def test_baseline_scenarios_match_expected_rule_outcomes(
    payload: dict[str, object], category: str, action: str
) -> None:
    response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    assert response.json()["threat_category"] == category
    assert response.json()["recommended_action"] == action
