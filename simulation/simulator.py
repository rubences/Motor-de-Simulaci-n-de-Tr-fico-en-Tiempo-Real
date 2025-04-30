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
        # Parámetros ajustables
        self.stop_distance = 10.0
        self.turn_threshold = 10.0

    def update_lights(self):
        t0 = time.perf_counter()
        for tl in self.city.traffic_lights:
            tl.update_state()
        self.stats["lights_times"].append(time.perf_counter() - t0)

    def update_vehicles(self):
        t0 = time.perf_counter()
        rows = self.city._rows
        cols = self.city._cols

        # 1) Control de semáforo y giro aleatorio al llegar a intersección
        for v in list(self.city.vehicles):
            x, y = v.position
            for inter in self.city.intersections:
                ix, iy = inter.pos
                if abs(x - ix) <= self.turn_threshold and abs(y - iy) <= self.turn_threshold:
                    state = inter.traffic_light.current_state
                    # Solo girar o seguir si no está en rojo
                    if state != "RED":
                        if v.direction in ("ESTE", "OESTE"):
                            v.direction = random.choice((v.direction, "NORTE", "SUR"))
                        else:
                            v.direction = random.choice((v.direction, "ESTE", "OESTE"))
                    # Rompemos para no procesar múltiples intersecciones
                    break

        # 2) Movimiento con control de semáforo
        for v in list(self.city.vehicles):
            x, y = v.position
            allowed = True

            # Horizontal (EASTE/OESTE)
            if v.direction in ("ESTE", "OESTE"):
                lane = rows.get(y, [])
                xs = [coord for coord, _ in lane]
                idx = (bisect.bisect_right(xs, x)
                       if v.direction == "ESTE"
                       else bisect.bisect_left(xs, x) - 1)
                if 0 <= idx < len(xs):
                    ix, inter = lane[idx]
                    # No avanzar si ROJO dentro de stop_distance
                    if abs(ix - x) <= self.stop_distance and inter.traffic_light.current_state == "RED":
                        allowed = False
            # Vertical (NORTE/SUR)
            else:
                lane = cols.get(x, [])
                ys = [coord for coord, _ in lane]
                idx = (bisect.bisect_right(ys, y)
                       if v.direction == "NORTE"
                       else bisect.bisect_left(ys, y) - 1)
                if 0 <= idx < len(ys):
                    iy, inter = lane[idx]
                    if abs(iy - y) <= self.stop_distance and inter.traffic_light.current_state == "RED":
                        allowed = False

            if allowed:
                v.move()
                # Clamp dentro de la ventana
                nx = max(0, min(v.position[0], SCREEN_WIDTH))
                ny = max(0, min(v.position[1], SCREEN_HEIGHT))
                v.position = (nx, ny)

        # 3) Despawn en los puntos negros
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
