# simulacion_trafico/main.py

import asyncio
import threading

from environment.City import City
from environment.Vehicle import Vehicle
from environment.TrafficLight import TrafficLight
from simulation.simulator import Simulator
from concurrency.tasks import simulation_loop
from ui.gui import launch_gui

def start_simulation(simulator, interval):
    asyncio.run(simulation_loop(simulator, interval))

def main():
    # Crear el entorno de la simulación
    city = City(name="Ciudad Ejemplo")

    # Crear semáforos y asignarles ids que coincidan con las posiciones en la GUI
    traffic_light_1 = TrafficLight(id_="T1", green_time=4, yellow_time=1, red_time=3)
    traffic_light_2 = TrafficLight(id_="T2", green_time=5, yellow_time=1, red_time=4)

    # Crear vehículos con posiciones iniciales (en coordenadas de la GUI)
    vehicle_1 = Vehicle(id_="V1", position=(50, 300), speed=2.0, direction="NORTE")
    vehicle_2 = Vehicle(id_="V2", position=(150, 300), speed=3.0, direction="OESTE")

    city.add_traffic_light(traffic_light_1)
    city.add_traffic_light(traffic_light_2)
    city.add_vehicle(vehicle_1)
    city.add_vehicle(vehicle_2)

    simulator = Simulator(city=city)

    # Iniciar la simulación en un hilo aparte (se ejecuta de forma asíncrona)
    sim_thread = threading.Thread(target=start_simulation, args=(simulator, 0.1), daemon=True)
    sim_thread.start()

    # Lanzar la GUI en el hilo principal
    launch_gui(simulator)

if __name__ == "__main__":
    main()


