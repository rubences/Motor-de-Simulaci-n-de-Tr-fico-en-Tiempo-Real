# main.py

import asyncio
import random
import math

from environment.City import City
from environment.TrafficLight import TrafficLight
from environment.Vehicle import Vehicle
from environment.road import Road, Intersection
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks
from ui.gui import launch_gui

async def spawn_loop(simulator, spawn_positions):
    """
    - Solo spawnea en spawn_positions (2 puntos horizontales).
    - Hasta 16 vehículos simultáneos.
    - Separación mínima de 50 px entre spawns.
    - Dirección inicial ESTE/OESTE hacia el centro.
    - Intervalo dinámico vía simulator.spawn_interval.
    """
    counter = 0
    spacing = 50

    # Primer retardo
    await asyncio.sleep(simulator.spawn_interval)

    while True:
        if len(simulator.city.vehicles) < 16:
            for px, py in spawn_positions:
                if any(math.hypot(v.position[0]-px, v.position[1]-py) < spacing
                       for v in simulator.city.vehicles):
                    continue
                mid_x = (spawn_positions[0][0] + spawn_positions[1][0]) / 2
                direction = "ESTE" if px < mid_x else "OESTE"
                v = Vehicle(
                    f"V{counter}",
                    position=(px, py),
                    speed=simulator.default_speed,
                    direction=direction
                )
                simulator.city.add_vehicle(v)
                counter += 1
                break

        await asyncio.sleep(simulator.spawn_interval)

async def main():
    # 1) Crear ciudad y definir carreteras
    city = City("Ciudad Ejemplo")
    # Horizontal
    city.add_road(Road((50, 300), (750, 300)))
    # Vertical izquierda y derecha
    city.add_road(Road((300, 50), (300, 550)))
    city.add_road(Road((500, 50), (500, 550)))

    # 2) Semáforos en cruces centrales
    tl1 = TrafficLight("TL1"); i1 = Intersection((300, 300), tl1)
    city.add_intersection(i1); city.add_traffic_light(tl1)
    tl2 = TrafficLight("TL2"); i2 = Intersection((500, 300), tl2)
    city.add_intersection(i2); city.add_traffic_light(tl2)

    # 3) Vehículos de prueba (opcional)
    city.add_vehicle(Vehicle("V1", (100, 300), speed=2, direction="ESTE"))
    city.add_vehicle(Vehicle("V2", (700, 300), speed=2, direction="OESTE"))

    # 4) Instanciar simulador y parámetros dinámicos
    simulator = Simulator(city)
    # Despawn en 6 puntos (círculos negros)
    despawn_pts = [
        (50, 300), (750, 300),    # extremos horizontales
        (300, 50), (300, 550),    # extremos vertical izqda
        (500, 50), (500, 550)     # extremos vertical drcha
    ]
    simulator.spawn_points = despawn_pts

    # Spawn 50px dentro de los extremos horizontales
    spawn_positions = [(50+50, 300), (750-50, 300)]

    simulator.spawn_interval = 0.5
    simulator.default_speed  = 2.0

    # 5) Tareas base de simulación
    sim_tasks = run_simulation_tasks(
        simulator,
        vehicle_interval=0.1,
        light_interval=1.0,
        metrics_interval=5.0
    )

    # 6) Lanzar spawn_loop y GUI
    spawn_task = asyncio.create_task(spawn_loop(simulator, spawn_positions))
    gui_task   = asyncio.create_task(launch_gui(simulator))

    # 7) Tras cerrar la GUI, cancelar tareas
    await gui_task
    sim_tasks[2].cancel()  # métricas
    spawn_task.cancel()
    for t in sim_tasks:
        t.cancel()
    await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
