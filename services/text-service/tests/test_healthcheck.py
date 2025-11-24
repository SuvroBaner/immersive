from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthcheck_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "text-service"
    }
