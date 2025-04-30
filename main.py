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
    - Hasta 16 vehículos.
    - spawn_positions: 4 puntos, cada uno 50px dentro de los círculos negros.
    - Separación mínima de 50px.
    - Dirección inicial según el eje: E/W o N/S hacia el centro.
    """
    counter = 0
    spacing = 50
    await asyncio.sleep(simulator.spawn_interval)

    while True:
        if len(simulator.city.vehicles) < 16:
            for px, py in spawn_positions:
                if any(math.hypot(v.position[0]-px, v.position[1]-py) < spacing
                       for v in simulator.city.vehicles):
                    continue
                # Decide dirección inicial según spawn_position
                # Si spawn_positions x es variable → horizontal, si y variable → vertical
                mid_x = (spawn_positions[0][0] + spawn_positions[1][0]) / 2
                mid_y = (spawn_positions[2][1] + spawn_positions[3][1]) / 2
                if px != px: pass  # dummy
                # Si spawn es lateral:
                if py == spawn_positions[0][1]:
                    direction = "ESTE" if px < mid_x else "OESTE"
                else:
                    # spawn vertical arriba/abajo
                    direction = "NORTE" if py < mid_y else "SUR"
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
    # 1) Ciudad y vías
    city = City("Ciudad Ejemplo")
    city.add_road(Road((50, 300), (750, 300)))    # horizontal
    city.add_road(Road((300, 50), (300, 550)))    # vertical extendida
    city.add_road(Road((500, 50), (500, 550)))    # vertical extendida

    tl1 = TrafficLight("TL1"); i1 = Intersection((300, 300), tl1)
    city.add_intersection(i1); city.add_traffic_light(tl1)
    tl2 = TrafficLight("TL2"); i2 = Intersection((500, 300), tl2)
    city.add_intersection(i2); city.add_traffic_light(tl2)

    # 2) Simulador
    simulator = Simulator(city)

    # Despawn points (círculos negros) en 6 extremos (incluimos la carretera paralela)
    despawn_pts = [
        (50, 300),  # inicio horizontal izquierda
        (750, 300), # fin horizontal derecha
        (300, 50),  # inicio vertical x=300 arriba
        (300, 550), # fin vertical x=300 abajo
        (500, 50),  # inicio vertical x=500 arriba
        (500, 550)  # fin vertical x=500 abajo
    ]
    simulator.spawn_points = despawn_pts

    # Spawn positions 50px dentro de cada círculo negro
    offset = 50
    spawn_positions = [
        (50  + offset, 300),     # horizontal izquierda
        (750 - offset, 300),     # horizontal derecha
        (300, 50  + offset),     # vertical x=300 arriba
        (300, 550 - offset),     # vertical x=300 abajo
        (500, 50  + offset),     # vertical x=500 arriba
        (500, 550 - offset),     # vertical x=500 abajo
    ]

    simulator.spawn_interval = 0.5 
    simulator.default_speed  = 2.0

    # 3) Tareas base
    sim_tasks = run_simulation_tasks(
        simulator,
        vehicle_interval=0.1,
        light_interval=1.0,
        metrics_interval=5.0
    )

    # 4) Spawn y GUI
    spawn_task = asyncio.create_task(spawn_loop(simulator, spawn_positions))
    gui_task   = asyncio.create_task(launch_gui(simulator))

    # 5) Al cerrar
    await gui_task
    sim_tasks[2].cancel()
    spawn_task.cancel()
    for t in sim_tasks:
        t.cancel()
    await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
