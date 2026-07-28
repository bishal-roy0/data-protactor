from fastapi.testclient import TestClient

from sentinel_ai.main import app


client = TestClient(app)


def test_health_check_returns_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "Karna",
        "environment": "development",
    }


def test_dashboard_is_available() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Karna" in response.text


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
    assert payload["recommended_action"] == "quarantine"


def test_analyze_returns_safe_result_without_signals() -> None:
    response = client.post("/analyze", json={"text": "See you at the team meeting tomorrow."})

    assert response.status_code == 200
    assert response.json()["risk_level"] == "safe"
    assert response.json()["recommended_action"] == "allow"


def test_analyze_detects_social_engineering() -> None:
    response = client.post(
        "/analyze",
        json={"text": "Please buy a gift card immediately and send the code."},
    )

    assert response.status_code == 200
    assert response.json()["threat_category"] == "social_engineering"


def test_analyze_flags_executable_download_url() -> None:
    response = client.post("/analyze", json={"urls": ["https://example.com/update.exe"]})

    assert response.status_code == 200
    assert response.json()["threat_category"] == "malware_download"
    assert response.json()["recommended_action"] == "block"


def test_image_analysis_returns_keyless_fallback() -> None:
    response = client.post(
        "/analyze/image",
        files={"image": ("safe.png", b"\x89PNG\r\n\x1a\nminimal", "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["risk_level"] == "safe"
    assert "OPENAI_API_KEY" in response.json()["summary"]


def test_image_analysis_rejects_unsupported_type() -> None:
    response = client.post(
        "/analyze/image",
        files={"image": ("payload.gif", b"GIF89a", "image/gif")},
    )

    assert response.status_code == 415


def test_image_analysis_rejects_large_file() -> None:
    large_png = b"\x89PNG\r\n\x1a\n" + (b"x" * (5 * 1024 * 1024))
    response = client.post(
        "/analyze/image",
        files={"image": ("large.png", large_png, "image/png")},
    )

    assert response.status_code == 413
