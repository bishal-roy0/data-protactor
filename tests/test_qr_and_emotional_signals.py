from fastapi.testclient import TestClient

from sentinel_ai.main import app

client = TestClient(app)
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"test"


def test_emotional_pretext_with_sensitive_request_is_flagged() -> None:
    response = client.post("/analyze", json={"text": "I heard your company is downsizing. Verify your identity immediately to keep your job."})

    assert response.status_code == 200
    assert "Emotional-pressure pretext" in {item["signal"] for item in response.json()["evidence"]}


def test_emotional_support_without_risky_request_is_not_flagged() -> None:
    response = client.post("/analyze", json={"text": "I am sorry to hear about your loss. I am here if you want to talk."})

    assert response.status_code == 200
    assert "Emotional-pressure pretext" not in {item["signal"] for item in response.json()["evidence"]}


def test_qr_url_is_analyzed_without_network(monkeypatch) -> None:
    monkeypatch.setattr("sentinel_ai.services.qr_analyzer.QrAnalyzer._decode", staticmethod(lambda _image: "https://nu-cashback.link/"))

    response = client.post("/analyze/qr", files={"image": ("code.png", PNG_BYTES, "image/png")})

    assert response.status_code == 200
    assert response.json()["recommended_action"] == "block"
    assert response.json()["analysis_sources"] == ["local_qr_decoder", "local_rules"]


def test_qr_rejects_unsupported_image_type() -> None:
    response = client.post("/analyze/qr", files={"image": ("code.gif", b"GIF89a", "image/gif")})

    assert response.status_code == 415


def test_qr_rejects_large_image() -> None:
    response = client.post("/analyze/qr", files={"image": ("code.png", b"\x89PNG\r\n\x1a\n" + b"0" * (5 * 1024 * 1024), "image/png")})

    assert response.status_code == 413
