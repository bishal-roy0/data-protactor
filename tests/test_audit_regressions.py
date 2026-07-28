"""Regression coverage added during the production audit."""

import asyncio

import httpx
from fastapi.testclient import TestClient

from sentinel_ai.main import app
from sentinel_ai.services.image_analyzer import ImageAnalyzer
from sentinel_ai.services.reputation import VirusTotalReputationService

client = TestClient(app)


def test_prize_scam_is_labeled_as_scam() -> None:
    response = client.post(
        "/analyze",
        json={"text": "Congratulations, you have won a prize. Pay a processing fee now."},
    )

    assert response.status_code == 200
    assert response.json()["threat_category"] == "scam"


def test_deceptive_media_link_is_labeled_as_suspicious_url() -> None:
    response = client.post("/analyze", json={"urls": ["https://example.com/private-video"]})

    assert response.status_code == 200
    assert response.json()["threat_category"] == "suspicious_url"


def test_virustotal_failure_returns_no_reputation_evidence(monkeypatch) -> None:
    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, *_args, **_kwargs):
            raise httpx.ConnectError("provider unavailable")

    monkeypatch.setattr(
        "sentinel_ai.services.reputation.httpx.AsyncClient",
        lambda **_kwargs: FailingClient(),
    )

    evidence = asyncio.run(
        VirusTotalReputationService("test-key").evidence_for(["https://example.com"])
    )

    assert evidence == []


def test_openai_vision_failure_returns_structured_caution() -> None:
    class FailingResponses:
        async def create(self, **_kwargs):
            raise RuntimeError("provider unavailable")

    class FailingClient:
        responses = FailingResponses()

    analyzer = ImageAnalyzer("test-key", "test-model")
    analyzer._client = FailingClient()  # type: ignore[assignment]

    response = asyncio.run(analyzer.analyze(b"\x89PNG\r\n\x1a\nimage", "image/png"))

    assert response.risk_level == "low"
    assert response.recommended_action == "show_caution"
    assert "provider unavailable" not in response.summary
