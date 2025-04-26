# environment/City.py

from collections import defaultdict

class City:
    """
    Ciudad que contiene carreteras, intersecciones, semáforos y vehículos,
    con índices espaciales para búsquedas rápidas.
    """
    def __init__(self, name: str):
        self.name = name
        self.roads = []
        self.intersections = []
        self.traffic_lights = []
        self.vehicles = []
        # Índices para detección eficiente de semáforos
        self._rows = {}   # key = y, value = sorted list of (x, intersection)
        self._cols = {}   # key = x, value = sorted list of (y, intersection)

    def add_road(self, road):
        self.roads.append(road)

    def add_intersection(self, intersection):
        self.intersections.append(intersection)
        self.build_index()

    def add_traffic_light(self, traffic_light):
        self.traffic_lights.append(traffic_light)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def build_index(self):
        """
        Reconstruye los índices espaciales de intersecciones:
         - _rows[y] = [(x1, inter1), (x2, inter2), ...]
         - _cols[x] = [(y1, inter1), (y2, inter2), ...]
        """
        rows = defaultdict(list)
        cols = defaultdict(list)
        for inter in self.intersections:
            x, y = inter.pos
            rows[y].append((x, inter))
            cols[x].append((y, inter))
        # Ordenar
        self._rows = {y: sorted(lst, key=lambda t: t[0]) for y, lst in rows.items()}
        self._cols = {x: sorted(lst, key=lambda t: t[0]) for x, lst in cols.items()}

    def __str__(self):
        return (f"City: {self.name}, Roads: {len(self.roads)}, "
                f"Intersections: {len(self.intersections)}, "
                f"TrafficLights: {len(self.traffic_lights)}, "
                f"Vehicles: {len(self.vehicles)}")
