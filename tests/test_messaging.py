import pytest
from simulation.city import Vehicle
from simulation.distributed_city import DistributedCity
from simulation.messaging import MigrationPublisher

class FakePublisher(MigrationPublisher):
    def __init__(self):
        self.published = []

    async def connect(self):
        pass

    async def publish(self, vehicle, from_zone, to_zone):
        self.published.append({
            "vehicle_id": vehicle.id,
            "from_zone": from_zone,
            "to_zone": to_zone,
            "position": vehicle.posicion
        })

    async def close(self):
        pass

@pytest.mark.asyncio
async def test_migration_publishing(tmp_path):
    zones_yaml = tmp_path / "zones.yaml"
    zones_yaml.write_text("""
zones:
  - name: left
    xmin: 0
    xmax: 10
    ymin: 0
    ymax: 10
  - name: right
    xmin: 10
    xmax: 20
    ymin: 0
    ymax: 10
""")
    publisher = FakePublisher()
    city = DistributedCity(str(zones_yaml), publisher)
    
    # Creamos un vehículo que se mueve +2 en X cada vez
    class TestVehicle(Vehicle):
        def mover(self):
            x, y = self.posicion
            self.posicion = (x + 2, y)

    veh = TestVehicle("v1", (8, 5))
    city.add_vehicle(veh)

    # Simulamos dos pasos sin demora
    await city.simulate(steps=2, delay=0)

    # Debe haberse publicado un único evento de migración
    assert len(publisher.published) == 1
    event = publisher.published[0]
    assert event["vehicle_id"] == "v1"
    assert event["from_zone"] == "left"
    assert event["to_zone"] == "right"
    assert event["position"] == (10, 5)
