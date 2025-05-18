#!/usr/bin/env python3
import argparse
import time
from prometheus_client import start_http_server, Gauge

# Intentamos importar DistributedCity; si falla, usamos modo dummy
try:
    from simulation.city import DistributedCity
    HAS_CITY = True
except ImportError:
    HAS_CITY = False
    print("⚠️  Módulo simulation.city no encontrado; entrando en modo métricas dummy")

class Simulator:
    """
    Orquesta semáforos y vehículos con métodos para snapshot gráfico.
    """
    def __init__(self, city, zone_name="unknown"):
        self.city = city
        self.zone = zone_name
        self.stats = {"lights_times": [], "vehicles_times": []}
        self.spawn_points = getattr(city, "spawn_points", [])
        self.stop_distance = 5.0
        self.turn_threshold = 5.0

        # Inicia servidor de métricas Prometheus en puerto 8001
        start_http_server(8001)
        self.sim_load = Gauge('node_load', 'Número de vehículos activos en la simulación', ['zone'])
        print(f"[Metrics] Prometheus server listening on 0.0.0.0:8001 for zone '{self.zone}'")

    def update_lights(self):
        t0 = time.perf_counter()
        for tl in self.city.traffic_lights:
            tl.update_state()
        self.stats["lights_times"].append(time.perf_counter() - t0)

    def update_vehicles(self):
        t0 = time.perf_counter()
        # Lógica trivial: mueve cada vehículo
        for v in list(self.city.vehicles):
            v.move()
            x, y = v.position
            v.position = (max(0, min(799, x)), max(0, min(599, y)))
        self.stats["vehicles_times"].append(time.perf_counter() - t0)

        # Actualiza métrica de carga
        current_count = len(self.city.vehicles)
        self.sim_load.labels(zone=self.zone).set(current_count)

    def get_snapshot(self):
        """Devuelve datos básicos de estado para APIs sin GUI."""
        return {
            "traffic_lights": [str(tl) for tl in self.city.traffic_lights],
            "vehicles":       [str(v) for v in self.city.vehicles]
        }

    def get_snapshot_graphic(self):
        """Devuelve datos de renderizado para la GUI."""
        return {
            "roads": [
                {"start": road.start, "end": road.end, "width": getattr(road, "width", 4)}
                for road in getattr(self.city, 'roads', [])
            ],
            "intersections": [
                {"pos": inter.pos, "light_state": inter.traffic_light.current_state}
                for inter in self.city.intersections
            ],
            "vehicles": [
                {"pos": v.position, "id": v.id_, "direction": v.direction}
                for v in self.city.vehicles
            ]
        }


def dummy_metrics(zone):
    """
    Genera métricas dummy para verificar el endpoint.
    """
    start_http_server(8001)
    gauge = Gauge('node_load', 'Dummy metric for load testing', ['zone'])
    n = 0
    print(f"[Dummy] Prometheus server on 0.0.0.0:8001 for zone '{zone}'")
    while True:
        gauge.labels(zone=zone).set(n % 100)
        n += 1
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Simulador de tráfico distribuido por zona")
    parser.add_argument("--zone", required=True, help="Nombre de la zona a simular")
    args = parser.parse_args()
    zone = args.zone

    if not HAS_CITY:
        dummy_metrics(zone)
        return

    # Instancia tu ciudad real
    city = DistributedCity(config_file='config/zones.yaml', zone=zone)
    sim = Simulator(city, zone_name=zone)
    print(f"Simulación iniciada para zona '{zone}'")

    try:
        while True:
            sim.update_lights()
            sim.update_vehicles()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Simulación detenida por usuario.")


if __name__ == "__main__":
    main()
