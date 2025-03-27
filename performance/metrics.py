# simulacion_trafico/performance/metrics.py

import logging

logging.basicConfig(level=logging.INFO)

def log_simulation_state(simulator):
    snapshot = simulator.get_snapshot()
    logging.info("Estado de la simulación: %s", snapshot)

