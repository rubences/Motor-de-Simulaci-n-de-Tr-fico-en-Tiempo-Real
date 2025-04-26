# ui/gui.py

import pygame
import asyncio

def draw_roads(screen, roads):
    """
    Dibuja cada carretera como una línea gris.
    """
    for r in roads:
        pygame.draw.line(
            screen,
            (200, 200, 200),
            r["start"],
            r["end"],
            r.get("width", 4)
        )

def draw_intersections(screen, intersections):
    """
    Dibuja cada intersección como un círculo cuyo color refleja el estado del semáforo.
    """
    for inter in intersections:
        x, y = inter["pos"]
        state = inter["light_state"]
        color = {
            "GREEN": (0, 255, 0),
            "YELLOW": (255, 255, 0),
            "RED": (255, 0, 0)
        }.get(state, (255, 255, 255))
        pygame.draw.circle(screen, color, (x, y), 8)

def draw_vehicles(screen, vehicles):
    """
    Dibuja cada vehículo como un círculo azul.
    """
    for v in vehicles:
        pygame.draw.circle(screen, (0, 0, 255), v["pos"], 5)

def run_pygame(simulator):
    """
    Bucle principal de Pygame que renderiza carreteras, intersecciones y vehículos.
    """
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Simulación de Tráfico")
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))
        state = simulator.get_snapshot_graphic()
        draw_roads(screen, state["roads"])
        draw_intersections(screen, state["intersections"])
        draw_vehicles(screen, state["vehicles"])

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

async def launch_gui(simulator):
    """
    Lanza el renderer de Pygame en un hilo separado para no bloquear asyncio.
    """
    await asyncio.to_thread(run_pygame, simulator)
