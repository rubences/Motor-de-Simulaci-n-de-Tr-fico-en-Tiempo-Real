# performance/metrics.py

import logging

logging.basicConfig(level=logging.INFO)

def log_simulation_state(simulator):
    """
    Muestra por consola el estado de la simulación + estadísticas de rendimiento.
    """
    snapshot = simulator.get_snapshot()
    # Calculamos promedios de los tiempos medidos
    lt = simulator.stats["lights_times"]
    vt = simulator.stats["vehicles_times"]
    avg_lt = sum(lt)/len(lt) if lt else 0
    avg_vt = sum(vt)/len(vt) if vt else 0

    logging.info(f"Estado de la simulación: {snapshot} | "
                 f"Avg lights update: {avg_lt:.6f}s | "
                 f"Avg vehicles update: {avg_vt:.6f}s")

    # Limpiamos los acumulados para la siguiente tanda
    lt.clear()
    vt.clear()
