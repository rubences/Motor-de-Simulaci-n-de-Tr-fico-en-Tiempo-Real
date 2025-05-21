import pytest
from fastapi.testclient import TestClient

from services.coordinator_service.main import app, zone_loads

@pytest.fixture(autouse=True)
def clear_loads():
    # Antes de cada test, vaciamos el estado de cargas
    zone_loads.clear()

def test_assign_without_reports():
    client = TestClient(app)
    response = client.get("/assign")
    assert response.status_code == 200
    assert response.json() == {"zone": None}

def test_report_and_assign():
    client = TestClient(app)
    # Reportamos carga de dos zonas
    r1 = client.post("/report_load", json={"zone": "A", "load": 10})
    assert r1.status_code == 200 and r1.json() == {"status": "received"}

    r2 = client.post("/report_load", json={"zone": "B", "load": 5})
    assert r2.status_code == 200 and r2.json() == {"status": "received"}

    # Ahora /assign debería devolver "B" (es la zona de menor carga)
    a1 = client.get("/assign")
    assert a1.status_code == 200
    assert a1.json() == {"zone": "B"}

    # Actualizamos carga de "A" para que sea la menor
    client.post("/report_load", json={"zone": "A", "load": 2})
    a2 = client.get("/assign")
    assert a2.json() == {"zone": "A"}
