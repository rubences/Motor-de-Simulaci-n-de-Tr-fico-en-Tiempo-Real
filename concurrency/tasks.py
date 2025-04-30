import asyncio
from performance.metrics import log_simulation_state

async def vehicles_loop(simulator, interval: float = 0.1):
    """
    Cada tick mueve los vehículos respetando semáforos.
    """
    while True:
        simulator.update_vehicles()
        await asyncio.sleep(interval)

async def traffic_lights_loop(simulator, interval: float = 1.0):
    """
    Cada tick actualiza el estado de los semáforos.
    """
    while True:
        simulator.update_lights()
        await asyncio.sleep(interval)

async def metrics_loop(simulator, interval: float = 5.0):
    """
    Cada tick registra métricas de rendimiento.
    """
    while True:
        log_simulation_state(simulator)
        await asyncio.sleep(interval)

def run_simulation_tasks(
    simulator,
    vehicle_interval: float = 0.1,
    light_interval: float   = 1.0,
    metrics_interval: float = 5.0,
    spawner=None,
    spawn_interval: float = None
):
    """
    Crea y devuelve las tareas asyncio:
      - vehicles_loop
      - traffic_lights_loop
      - metrics_loop
      - spawn_loop (opcional si se proporciona spawner y spawn_interval)
    """
    tasks = [
        asyncio.create_task(vehicles_loop(simulator, vehicle_interval)),
        asyncio.create_task(traffic_lights_loop(simulator, light_interval)),
        asyncio.create_task(metrics_loop(simulator, metrics_interval)),
    ]
    if spawner is not None and spawn_interval is not None:
        tasks.append(asyncio.create_task(spawner.spawn_loop(spawn_interval)))
    return tasks
