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
