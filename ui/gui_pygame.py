# simulacion_trafico/ui/gui_pygame.py

import pygame
from pygame.locals import *
import sys

def launch_pygame_gui(simulator):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Simulación de Tráfico en Tiempo Real con Pygame")
    clock = pygame.time.Clock()
    running = True

    # Colores
    WHITE  = (255, 255, 255)
    BLACK  = (0, 0, 0)
    RED    = (255, 0, 0)
    GREEN  = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BLUE   = (0, 0, 255)

    def get_traffic_light_color(state):
        if state == "GREEN":
            return GREEN
        elif state == "YELLOW":
            return YELLOW
        else:
            return RED

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Actualización de la pantalla
        screen.fill(WHITE)

        # Dibujar semáforos (se asignan posiciones fijas por ejemplo)
        for tl in simulator.city.traffic_lights:
            if tl.id_ == "T1":
                pos = (100, 100)
            elif tl.id_ == "T2":
                pos = (300, 100)
            else:
                pos = (50, 50)
            color = get_traffic_light_color(tl.current_state)
            pygame.draw.circle(screen, color, pos, 15)

        # Dibujar vehículos (se supone que v.position es una tupla (x, y) en coordenadas de pantalla)
        for v in simulator.city.vehicles:
            x, y = v.position
            rect = pygame.Rect(x - 10, y - 5, 20, 10)
            pygame.draw.rect(screen, BLUE, rect)

        pygame.display.flip()
        clock.tick(60)  # 60 fps

    pygame.quit()
    sys.exit()

