# simulation/simulator.py

import time
import bisect
import random

# Dimensiones de la ventana
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600

class Simulator:
    """
    Orquesta semáforos y vehículos,
    mide tiempos, permite giro aleatorio y despawn en spawn_points.
    """
    def __init__(self, city):
        self.city = city
        self.stats = {"lights_times": [], "vehicles_times": []}
        # Se inyecta desde main.py
        self.spawn_points = []

    def update_lights(self):
        t0 = time.perf_counter()
        for tl in self.city.traffic_lights:
            tl.update_state()
        self.stats["lights_times"].append(time.perf_counter() - t0)

    def update_vehicles(self,
                        stop_distance: float  = 10.0,
                        turn_threshold: float = 10.0):
        t0 = time.perf_counter()
        rows = self.city._rows
        cols = self.city._cols

        # 1) Giro aleatorio en semáforo (E/W → posibilidad de seguir recto o girar)
        for v in list(self.city.vehicles):
            x, y = v.position
            for inter in self.city.intersections:
                ix, iy = inter.pos
                if abs(x - ix) <= turn_threshold and abs(y - iy) <= turn_threshold:
                    if v.direction in ("ESTE", "OESTE"):
                        # ahora puede seguir recto o girar Norte/Sur
                        v.direction = random.choice((v.direction, "NORTE", "SUR"))
                    break

        # 2) Movimiento con control de semáforo y clamp a ventana
        for v in list(self.city.vehicles):
            x, y = v.position
            allowed = True

            if v.direction in ("ESTE", "OESTE"):
                lane = rows.get(y, [])
                xs = [xi for xi, _ in lane]
                idx = (bisect.bisect_right(xs, x)
                       if v.direction == "ESTE"
                       else bisect.bisect_left(xs, x) - 1)
                if 0 <= idx < len(xs):
                    ix, inter = lane[idx]
                    if abs(ix - x) <= stop_distance and inter.traffic_light.current_state == "RED":
                        allowed = False
            else:  # NORTE o SUR
                lane = cols.get(x, [])
                ys = [yi for yi, _ in lane]
                idx = (bisect.bisect_right(ys, y)
                       if v.direction == "NORTE"
                       else bisect.bisect_left(ys, y) - 1)
                if 0 <= idx < len(ys):
                    iy, inter = lane[idx]
                    if abs(iy - y) <= stop_distance and inter.traffic_light.current_state == "RED":
                        allowed = False

            if allowed:
                v.move()
                # Clamp dentro de la ventana
                nx = max(0, min(v.position[0], SCREEN_WIDTH))
                ny = max(0, min(v.position[1], SCREEN_HEIGHT))
                v.position = (nx, ny)

        # 3) Despawn en los 4 spawn_points (círculos negros)
        despawn_thresh = 8
        to_remove = []
        for v in self.city.vehicles:
            x, y = v.position
            for px, py in self.spawn_points:
                if abs(x - px) <= despawn_thresh and abs(y - py) <= despawn_thresh:
                    to_remove.append(v)
                    break
        for v in to_remove:
            self.city.vehicles.remove(v)
            print(f"[DEBUG] Se ha borrado {v.id_}")

        # 4) Registrar tiempo
        self.stats["vehicles_times"].append(time.perf_counter() - t0)

    def get_snapshot(self):
        return {
            "traffic_lights": [str(tl) for tl in self.city.traffic_lights],
            "vehicles":       [str(v)  for v  in self.city.vehicles]
        }

    def get_snapshot_graphic(self):
        return {
            "roads": [
                {"start": r.start, "end": r.end, "width": getattr(r, "width", 4)}
                for r in self.city.roads
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
