from fastapi.testclient import TestClient

from sentinel_ai.main import app


client = TestClient(app)


def test_health_check_returns_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "Sentinel AI",
        "environment": "development",
    }


def test_analyze_rejects_empty_content() -> None:
    response = client.post("/analyze", json={})

    assert response.status_code == 422


def test_analyze_detects_phishing_signals() -> None:
    response = client.post(
        "/analyze",
        json={"text": "Urgent: verify your account immediately with your OTP."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_score"] >= 70
    assert payload["risk_level"] == "critical"
    assert payload["threat_category"] == "phishing"
    assert payload["recommended_action"] == "block"


def test_analyze_returns_safe_result_without_signals() -> None:
    response = client.post("/analyze", json={"text": "See you at the team meeting tomorrow."})

    assert response.status_code == 200
    assert response.json()["risk_level"] == "safe"
    assert response.json()["recommended_action"] == "allow"
