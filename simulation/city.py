# simulation/city.py

class TrafficLight:
    def __init__(self):
        self.current_state = "GREEN"
    def update_state(self):
        # Alterna de forma trivial para demo
        self.current_state = "RED" if self.current_state == "GREEN" else "GREEN"

class Vehicle:
    def __init__(self, id_, position=(0,0), direction="ESTE"):
        self.id_ = id_
        self.position = position
        self.direction = direction
    def move(self):
        # Movimiento sencillo: avanza +1 en x si va ESTE, -1 si va OESTE, etc.
        x,y = self.position
        if self.direction == "ESTE":
            self.position = (x+1, y)
        elif self.direction == "OESTE":
            self.position = (x-1, y)
        elif self.direction == "NORTE":
            self.position = (x, y+1)
        else:
            self.position = (x, y-1)

class DistributedCity:
    """
    Stub de ciudad distribuida.
    Genera unos semáforos y vehículos iniciales para demo.
    """
    def __init__(self, config_file: str, zone: str):
        self.zone = zone
        # Puntos de spawn/despawn
        self.spawn_points = [(0,0), (799,599)]
        # Definimos unos semáforos e intersecciones fijas
        self.traffic_lights = [TrafficLight() for _ in range(4)]
        self.intersections = []
        # Un par de vehículos iniciales
        self.vehicles = [Vehicle(f"v{i}", position=(i*10, i*10)) for i in range(5)]
        # Mapa de filas y columnas para demo (vacío)
        self._rows = {}
        self._cols = {}
        # Líneas de carretera (para get_snapshot_graphic)
        self.roads = []
        # Inicializamos el mapa de filas y columnas