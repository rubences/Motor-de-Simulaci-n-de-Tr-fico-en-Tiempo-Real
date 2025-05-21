import yaml
import asyncio
from simulation.city import City, Vehicle
from simulation.messaging import MigrationPublisher

class Zone:
    def __init__(self, name: str, xmin: int, xmax: int, ymin: int, ymax: int):
        self.name = name
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def contains(self, vehicle: Vehicle) -> bool:
        x, y = vehicle.posicion
        return self.xmin <= x < self.xmax and self.ymin <= y < self.ymax

class DistributedCity(City):
    def __init__(
        self,
        zones_config_path: str,
        publisher: MigrationPublisher = None,
        width: int = 1000,
        height: int = 1000
    ):
        super().__init__(width=width, height=height)
        # Carga de zonas desde YAML
        with open(zones_config_path, 'r') as f:
            data = yaml.safe_load(f)
        self.zones = [Zone(**zone) for zone in data.get('zones', [])]
        # Publisher opcional para migraciones
        self.publisher = publisher

    def get_zone_for_vehicle(self, vehicle: Vehicle) -> Zone | None:
        for zone in self.zones:
            if zone.contains(vehicle):
                return zone
        return None

    async def simulate(self, steps: int = 100, delay: float = 0.1):
        # Si hay publisher, lo conectamos
        if self.publisher:
            await self.publisher.connect()

        # Estado inicial de zonas
        prev_zones = {
            v.id: (self.get_zone_for_vehicle(v).name if self.get_zone_for_vehicle(v) else None)
            for v in self.vehicles
        }

        for _ in range(steps):
            for v in self.vehicles:
                v.mover()
                cur_zone = self.get_zone_for_vehicle(v)
                cur_name = cur_zone.name if cur_zone else None
                prev_name = prev_zones.get(v.id)

                # Si cambió de zona y hay publisher, publicamos la migración
                if cur_name != prev_name and self.publisher:
                    await self.publisher.publish(v, prev_name, cur_name)
                    prev_zones[v.id] = cur_name

            await asyncio.sleep(delay)

        # Cerramos publisher si existía
        if self.publisher:
            await self.publisher.close()
