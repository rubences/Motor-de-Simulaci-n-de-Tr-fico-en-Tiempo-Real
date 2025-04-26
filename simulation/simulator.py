# simulation/simulator.py

import time
import bisect

class Simulator:
    """
    Orquesta las actualizaciones de semáforos y vehículos,
    midiendo tiempos y usando índices espaciales para semáforos.
    """
    def __init__(self, city):
        self.city = city
        self.stats = {
            "lights_times": [],
            "vehicles_times": []
        }

    def update_lights(self):
        start = time.perf_counter()
        for tl in self.city.traffic_lights:
            tl.update_state()
        self.stats["lights_times"].append(time.perf_counter() - start)

    def update_vehicles(self, stop_distance: float = 10.0):
        start = time.perf_counter()
        rows = self.city._rows
        cols = self.city._cols

        for v in self.city.vehicles:
            x, y = v.position
            move_allowed = True

            # Horizontal
            if v.direction in ("ESTE", "OESTE"):
                lane = rows.get(y)
                if lane:
                    xs = [xi for xi, _ in lane]
                    if v.direction == "ESTE":
                        idx = bisect.bisect_right(xs, x)
                    else:  # OESTE
                        idx = bisect.bisect_left(xs, x) - 1
                    if 0 <= idx < len(xs):
                        ix, inter = lane[idx]
                        if abs(ix - x) <= stop_distance and inter.traffic_light.current_state == "RED":
                            move_allowed = False

            # Vertical
            elif v.direction in ("NORTE", "SUR"):
                lane = cols.get(x)
                if lane:
                    ys = [yi for yi, _ in lane]
                    if v.direction == "NORTE":
                        idx = bisect.bisect_right(ys, y)
                    else:  # SUR
                        idx = bisect.bisect_left(ys, y) - 1
                    if 0 <= idx < len(ys):
                        iy, inter = lane[idx]
                        if abs(iy - y) <= stop_distance and inter.traffic_light.current_state == "RED":
                            move_allowed = False

            if move_allowed:
                v.move()

        self.stats["vehicles_times"].append(time.perf_counter() - start)

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
