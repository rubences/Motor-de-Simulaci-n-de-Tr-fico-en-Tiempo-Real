import asyncio
from environment.City import City
from environment.TrafficLight import TrafficLight
from environment.Vehicle import Vehicle
from environment.road import Road, Intersection
from simulation.simulator import Simulator
from concurrency.tasks import run_simulation_tasks
from ui.gui import launch_gui

async def main():
    # 1. Crear la ciudad
    city = City("Ciudad Ejemplo")

    # 2. Definir carreteras
    city.add_road(Road((100, 300), (700, 300)))  # horizontal
    city.add_road(Road((300, 100), (300, 500)))  # vertical izq.
    city.add_road(Road((500, 100), (500, 500)))  # vertical dcha.

    # 3. Crear semáforos e intersecciones
    tl1 = TrafficLight("TL1")
    inter1 = Intersection((300, 300), tl1)
    city.add_intersection(inter1)
    city.add_traffic_light(tl1)

    tl2 = TrafficLight("TL2")
    inter2 = Intersection((500, 300), tl2)
    city.add_intersection(inter2)
    city.add_traffic_light(tl2)

    # 4. Añadir vehículos de prueba
    city.add_vehicle(Vehicle("V1", (100, 300), speed=2, direction="ESTE"))
    city.add_vehicle(Vehicle("V2", (700, 300), speed=2, direction="OESTE"))

    # 5. Crear simulador
    simulator = Simulator(city)

    # 6. Lanzar tareas de simulación (sin mensajería)
    tasks = run_simulation_tasks(
        simulator,
        vehicle_interval=0.1,
        light_interval=1.0,
        metrics_interval=5.0
    )

    # 7. Iniciar GUI de Pygame en hilo aparte
    gui_task = asyncio.create_task(launch_gui(simulator))

    # 8. Ejecutar todo en paralelo
    await asyncio.gather(*tasks, gui_task)

if __name__ == "__main__":
    asyncio.run(main())
