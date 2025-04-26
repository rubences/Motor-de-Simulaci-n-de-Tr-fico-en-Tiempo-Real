# simulacion_trafico/environment/road.py

from typing import Tuple, List

class Road:
    """
    Representa una calle entre dos puntos en el plano.
    """
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], width: int = 4):
        self.start: Tuple[int, int] = start
        self.end: Tuple[int, int] = end
        self.width: int = width

    def __repr__(self) -> str:
        return f"Road(start={self.start}, end={self.end}, width={self.width})"


class Intersection:
    """
    Representa una intersección en la ciudad, con un semáforo y carreteras conectadas.
    """
    def __init__(self, pos: Tuple[int, int], traffic_light):
        self.pos: Tuple[int, int] = pos
        self.traffic_light = traffic_light
        # Lista de carreteras que confluyen en esta intersección
        self.roads: List[Road] = []

    def add_road(self, road: Road) -> None:
        """Añade una carretera que conecta con esta intersección."""
        self.roads.append(road)

    def __repr__(self) -> str:
        state = getattr(self.traffic_light, 'current_state', None)
        return f"Intersection(pos={self.pos}, light_state={state}, roads={len(self.roads)})"
