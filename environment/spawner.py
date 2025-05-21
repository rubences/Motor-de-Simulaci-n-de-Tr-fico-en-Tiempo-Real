# environment/spawner.py

import random
import asyncio
from environment.Vehicle import Vehicle

class Spawner:
    """
    Clase que se encarga de generar vehículos dinámicamente en puntos de entrada.
    """
    def __init__(self, city, spawn_points, default_speed=2.0, default_direction="ESTE"):
        self.city = city
        self.spawn_points = spawn_points
        self.default_speed = default_speed
        self.default_direction = default_direction
        self.counter = 0

    def spawn_vehicle(self):
        """
        Crea un nuevo vehículo en un punto aleatorio de spawn_points y lo añade a la ciudad.
        """
        spawn_point = random.choice(self.spawn_points)
        vehicle_id = f"V{self.counter}"
        vehicle = Vehicle(
            vehicle_id,
            position=spawn_point,
            speed=self.default_speed,
            direction=self.default_direction
        )
        self.city.add_vehicle(vehicle)
        self.counter += 1

    async def spawn_loop(self, interval: float):
        """
        Corrutina que lanza vehículos periódicamente según el intervalo dado.
        """
        while True:
            self.spawn_vehicle()
            await asyncio.sleep(interval)
