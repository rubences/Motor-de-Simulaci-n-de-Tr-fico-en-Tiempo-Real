import pytest
from fastapi.testclient import TestClient

from services.vehicles_service.main import app as vehicles_app
from services.semaphores_service.main import app as semaphores_app
from services.coordinator_service.main import app as coordinator_app

@pytest.mark.parametrize("app, name", [
    (vehicles_app, "Vehicles"),
    (semaphores_app, "Semaphores"),
    (coordinator_app, "Coordinator"),
])
def test_health(app, name):
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200, f"{name} service health endpoint failed"
    assert response.json() == {"status": "ok"}, f"{name} service returned unexpected JSON"
