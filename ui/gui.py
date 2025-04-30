# ui/gui.py

import pygame
import asyncio

class Slider:
    """
    Slider UI para ajustar un float.
    """
    def __init__(self, x, y, width, min_val, max_val, initial, label):
        self.rect = pygame.Rect(x, y, width, 6)
        self.min, self.max = min_val, max_val
        self.value = initial
        self.label = label
        self.handle_x = x + (initial - min_val)/(max_val - min_val)*width
        self.handle_rect = pygame.Rect(self.handle_x-8, y-7, 16, 20)
        self.dragging = False
        self.font = pygame.font.SysFont(None, 24)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self.handle_rect.collidepoint(e.pos):
            self.dragging = True
        elif e.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif e.type == pygame.MOUSEMOTION and self.dragging:
            nx = max(self.rect.x, min(e.pos[0], self.rect.x+self.rect.width))
            self.handle_x = nx
            self.handle_rect.x = nx-8
            rel = (nx-self.rect.x)/self.rect.width
            self.value = self.min + rel*(self.max-self.min)

    def draw(self, screen):
        pygame.draw.rect(screen, (150,150,150), self.rect)
        pygame.draw.rect(screen, (225,225,225), self.handle_rect)
        txt = f"{self.label}: {self.value:.2f}"
        surf = self.font.render(txt, True, (255,255,255))
        screen.blit(surf, (self.rect.x, self.rect.y-25))

def draw_roads(screen, roads):
    for r in roads:
        pygame.draw.line(screen, (200,200,200), r["start"], r["end"], r.get("width",4))

def draw_intersections(screen, intersections):
    for inter in intersections:
        col = (0,255,0) if inter["light_state"]=="GREEN" else \
              (255,255,0) if inter["light_state"]=="YELLOW" else \
              (255,0,0)
        pygame.draw.circle(screen, col, inter["pos"], 10)

def draw_vehicles(screen, vehicles):
    for v in vehicles:
        pygame.draw.circle(screen, (0,0,255), v["pos"], 6)

def run_pygame(simulator):
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Simulación de Tráfico")
    clock = pygame.time.Clock()

    spawn_slider = Slider(50, 520, 700, 0.1, 2.0, simulator.spawn_interval, "Spawn Interval (s)")
    speed_slider = Slider(50, 560, 700, 1.0, 5.0, simulator.default_speed,   "Vehicle Speed")

    despawn_pts = simulator.spawn_points

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            spawn_slider.handle_event(e)
            speed_slider.handle_event(e)

        # Aplicar cambios
        simulator.spawn_interval = spawn_slider.value
        simulator.default_speed   = speed_slider.value

        screen.fill((30,30,30))
        state = simulator.get_snapshot_graphic()

        draw_roads(screen, state["roads"])
        draw_intersections(screen, state["intersections"])
        draw_vehicles(screen, state["vehicles"])

        # Dibujar todos los despawn points
        for px, py in despawn_pts:
            pygame.draw.circle(screen, (255,255,255), (px,py), 10)
            pygame.draw.circle(screen, (0,0,0),       (px,py),  8)

        spawn_slider.draw(screen)
        speed_slider.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

async def launch_gui(simulator):
    await asyncio.to_thread(run_pygame, simulator)
