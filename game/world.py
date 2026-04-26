"""Elementos del mundo: mapa, objetos y zonas."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from game import settings
from game.entities import Enemy


@dataclass
class Treasure:
    rect: pygame.Rect
    value: int
    collected: bool = False


@dataclass
class ExplosiveTrap:
    rect: pygame.Rect
    damage: int
    triggered: bool = False


@dataclass
class ObjectiveZone:
    name: str
    rect: pygame.Rect
    completed: bool = False


@dataclass
class Decoration:
    rect: pygame.Rect
    color: tuple[int, int, int]
    kind: str


class World:
    def __init__(self, difficulty: str = "normal", floor: int = 1) -> None:
        self.difficulty = difficulty if difficulty in ("easy", "normal", "hard") else "normal"
        self.floor = max(1, floor)
        self.layouts = self._layout_catalog()
        self.layout = self.layouts[(self.floor - 1) % len(self.layouts)]
        self.walls = self._build_walls()
        self._validate_chamber_accessibility()
        self.decorations = self._spawn_decorations()
        self.enemies = self._spawn_enemies()
        self.treasures = self._spawn_treasures()
        self.traps = self._spawn_traps()
        self.objective_zones = self._spawn_objective_zones()
        self.shop_zone = self.layout["shop_zone"].copy()

    def _layout_catalog(self) -> list[dict]:
        return [
            {
                "name": "Ruinas Clasicas",
                "walls": [
                    pygame.Rect(180, 120, 200, 20),
                    pygame.Rect(440, 200, 20, 200),
                    pygame.Rect(610, 110, 260, 20),
                    pygame.Rect(250, 450, 250, 20),
                    pygame.Rect(620, 350, 20, 190),
                ],
                "enemy_specs": [
                    (120, 200, 70, "terrestre"),
                    (520, 130, 90, "volador"),
                    (720, 250, 80, "terrestre"),
                    (330, 520, 95, "volador"),
                    (760, 520, 110, "mini_jefe"),
                ],
                "treasure_positions": [(90, 560), (390, 80), (875, 90), (705, 565)],
                "trap_positions": [((280, 200), 10), ((560, 430), 14), ((820, 300), 12)],
                "zones": [
                    ("Sector Norte", pygame.Rect(40, 40, 320, 200)),
                    ("Ruinas Centrales", pygame.Rect(380, 170, 250, 260)),
                    ("Santuario Sur", pygame.Rect(640, 430, 260, 170)),
                ],
                "decorations": [
                    Decoration(pygame.Rect(75, 85, 16, 40), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(132, 74, 18, 18), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(330, 78, 18, 18), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(472, 72, 16, 40), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(666, 82, 18, 18), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(862, 74, 16, 40), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(116, 450, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(210, 532, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(500, 482, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(760, 472, 28, 8), (84, 94, 114), "rune"),
                ],
                "shop_zone": pygame.Rect(780, 520, 130, 90),
            },
            {
                "name": "Pasillos Gemelos",
                "walls": [
                    # Muros verticales divisores con huecos para acceso
                    pygame.Rect(280, 90, 20, 150),
                    pygame.Rect(280, 340, 20, 170),
                    pygame.Rect(660, 90, 20, 150),
                    pygame.Rect(660, 340, 20, 170),
                    # Muros horizontales superior e inferior
                    pygame.Rect(300, 90, 360, 20),
                    pygame.Rect(300, 490, 360, 20),
                    # Muro central dividido con hueco en el medio para acceso al jefe
                    pygame.Rect(450, 240, 60, 50),
                    pygame.Rect(450, 340, 60, 40),
                ],
                "enemy_specs": [
                    (120, 140, 80, "terrestre"),
                    (160, 470, 90, "volador"),
                    (770, 130, 85, "terrestre"),
                    (780, 470, 95, "volador"),
                    (470, 320, 120, "mini_jefe"),
                ],
                "treasure_positions": [(90, 80), (90, 560), (860, 80), (860, 560)],
                "trap_positions": [((240, 320), 10), ((480, 210), 13), ((720, 320), 12)],
                "zones": [
                    ("Ala Oeste", pygame.Rect(40, 40, 250, 560)),
                    ("Nucleo", pygame.Rect(300, 120, 360, 360)),
                    ("Ala Este", pygame.Rect(670, 40, 230, 560)),
                ],
                "decorations": [
                    Decoration(pygame.Rect(88, 170, 16, 38), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(88, 420, 16, 38), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(850, 170, 16, 38), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(850, 420, 16, 38), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(470, 140, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(470, 470, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(360, 310, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(560, 310, 28, 8), (84, 94, 114), "rune"),
                ],
                "shop_zone": pygame.Rect(430, 525, 130, 90),
            },
            {
                "name": "Anillo Profundo",
                "walls": [
                    # Anillo exterior con entradas en los cuatro lados
                    pygame.Rect(170, 120, 250, 20),
                    pygame.Rect(540, 120, 250, 20),
                    pygame.Rect(170, 500, 250, 20),
                    pygame.Rect(540, 500, 250, 20),
                    pygame.Rect(170, 140, 20, 130),
                    pygame.Rect(170, 350, 20, 150),
                    pygame.Rect(770, 140, 20, 130),
                    pygame.Rect(770, 350, 20, 150),
                    # Nucleo interior con huecos para combate cercano
                    pygame.Rect(350, 260, 100, 20),
                    pygame.Rect(510, 260, 100, 20),
                    pygame.Rect(350, 360, 100, 20),
                    pygame.Rect(510, 360, 100, 20),
                    pygame.Rect(470, 280, 20, 30),
                    pygame.Rect(470, 330, 20, 30),
                ],
                "enemy_specs": [
                    (240, 190, 120, "terrestre"),
                    (710, 190, 120, "volador"),
                    (240, 430, 120, "volador"),
                    (710, 430, 120, "terrestre"),
                    (445, 307, 100, "mini_jefe"),
                ],
                "treasure_positions": [(120, 320), (470, 90), (850, 320), (470, 545)],
                "trap_positions": [((320, 320), 11), ((470, 230), 14), ((620, 320), 11)],
                "zones": [
                    ("Arco Norte", pygame.Rect(190, 40, 580, 170)),
                    ("Camara Interna", pygame.Rect(230, 210, 500, 220)),
                    ("Arco Sur", pygame.Rect(190, 430, 580, 170)),
                ],
                "decorations": [
                    Decoration(pygame.Rect(210, 170, 16, 40), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(733, 170, 16, 40), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(210, 430, 16, 40), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(733, 430, 16, 40), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(460, 170, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(460, 430, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(350, 320, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(560, 320, 28, 8), (84, 94, 114), "rune"),
                ],
                "shop_zone": pygame.Rect(60, 525, 130, 90),
            },
            {
                "name": "Arena Antigua",
                "walls": [],
                "enemy_specs": [
                    (200, 130, 80, "terrestre"),
                    (750, 130, 80, "volador"),
                    (200, 500, 85, "volador"),
                    (750, 500, 85, "terrestre"),
                    (470, 320, 130, "mini_jefe"),
                ],
                "treasure_positions": [(120, 70), (840, 70), (120, 560), (840, 560)],
                "trap_positions": [((470, 120), 14), ((280, 320), 12), ((660, 320), 12)],
                "zones": [
                    ("Gradas Oeste", pygame.Rect(110, 90, 170, 400)),
                    ("Arena Central", pygame.Rect(310, 180, 360, 280)),
                    ("Gradas Este", pygame.Rect(720, 90, 110, 400)),
                ],
                "decorations": [
                    Decoration(pygame.Rect(200, 200, 16, 60), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(740, 200, 16, 60), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(470, 90, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(470, 510, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(400, 320, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(540, 320, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(110, 260, 8, 40), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(842, 260, 8, 40), (84, 94, 114), "rune"),
                ],
                "shop_zone": pygame.Rect(820, 540, 130, 80),
            },
            {
                "name": "Templo Perdido",
                "walls": [],
                "enemy_specs": [
                    (200, 120, 80, "volador"),
                    (750, 120, 80, "volador"),
                    (200, 500, 85, "terrestre"),
                    (750, 500, 85, "terrestre"),
                    (470, 310, 120, "mini_jefe"),
                ],
                "treasure_positions": [(120, 70), (840, 70), (120, 560), (840, 560)],
                "trap_positions": [((200, 300), 12), ((470, 150), 13), ((750, 300), 11)],
                "zones": [
                    ("Ala Oeste", pygame.Rect(110, 90, 180, 400)),
                    ("Santuario Central", pygame.Rect(330, 90, 280, 400)),
                    ("Ala Este", pygame.Rect(670, 90, 130, 400)),
                ],
                "decorations": [
                    Decoration(pygame.Rect(220, 200, 16, 60), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(720, 200, 16, 60), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(470, 100, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(470, 500, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(400, 310, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(540, 310, 28, 8), (84, 94, 114), "rune"),
                ],
                "shop_zone": pygame.Rect(20, 540, 130, 80),
            },
            {
                "name": "Catacumbas",
                "walls": [],
                "enemy_specs": [
                    (200, 140, 75, "terrestre"),
                    (720, 140, 75, "volador"),
                    (200, 500, 80, "volador"),
                    (720, 500, 80, "terrestre"),
                    (470, 310, 115, "mini_jefe"),
                ],
                "treasure_positions": [(120, 70), (840, 70), (120, 560), (840, 560)],
                "trap_positions": [((300, 260), 13), ((470, 120), 14), ((680, 300), 12)],
                "zones": [
                    ("Camara Oeste", pygame.Rect(110, 90, 180, 400)),
                    ("Nave Central", pygame.Rect(330, 90, 310, 400)),
                    ("Camara Este", pygame.Rect(700, 90, 110, 400)),
                ],
                "decorations": [
                    Decoration(pygame.Rect(160, 180, 16, 80), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(760, 180, 16, 80), (122, 135, 155), "pillar"),
                    Decoration(pygame.Rect(470, 100, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(470, 510, 20, 20), (255, 210, 120), "lamp"),
                    Decoration(pygame.Rect(300, 310, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(470, 310, 28, 8), (84, 94, 114), "rune"),
                    Decoration(pygame.Rect(680, 310, 28, 8), (84, 94, 114), "rune"),
                ],
                "shop_zone": pygame.Rect(820, 540, 130, 80),
            },
        ]

    def _build_walls(self) -> list[pygame.Rect]:
        border_walls = [
            pygame.Rect(0, 0, 960, 20),
            pygame.Rect(0, 620, 960, 20),
            pygame.Rect(0, 0, 20, 640),
            pygame.Rect(940, 0, 20, 640),
        ]
        return border_walls + [wall.copy() for wall in self.layout["walls"]]

    def _spawn_enemies(self) -> list[Enemy]:
        profile = settings.DIFFICULTY_PROFILES[self.difficulty]
        floor_hp_multiplier = 1.0 + (self.floor - 1) * 0.18
        floor_attack_multiplier = 1.0 + (self.floor - 1) * 0.12
        floor_speed_multiplier = min(1.7, 1.0 + (self.floor - 1) * 0.05)
        floor_profile = {
            **profile,
            "enemy_hp_multiplier": profile["enemy_hp_multiplier"] * floor_hp_multiplier,
            "enemy_attack_multiplier": profile["enemy_attack_multiplier"] * floor_attack_multiplier,
            "enemy_speed_multiplier": profile["enemy_speed_multiplier"] * floor_speed_multiplier,
        }
        enemy_specs = self.layout["enemy_specs"]

        return [
            Enemy(x, y, patrol_width=patrol_width, enemy_type=enemy_type, difficulty_profile=floor_profile)
            for x, y, patrol_width, enemy_type in enemy_specs
        ]

    def _spawn_treasures(self) -> list[Treasure]:
        profile = settings.DIFFICULTY_PROFILES[self.difficulty]
        values = [25, 35, 40, 30]
        floor_treasure_multiplier = 1.0 + (self.floor - 1) * 0.12
        values = [max(10, int(value * profile["treasure_multiplier"])) for value in values]
        values = [max(10, int(value * floor_treasure_multiplier)) for value in values]
        positions = self.layout["treasure_positions"]
        return [
            Treasure(pygame.Rect(positions[0][0], positions[0][1], 20, 20), value=values[0]),
            Treasure(pygame.Rect(positions[1][0], positions[1][1], 20, 20), value=values[1]),
            Treasure(pygame.Rect(positions[2][0], positions[2][1], 20, 20), value=values[2]),
            Treasure(pygame.Rect(positions[3][0], positions[3][1], 20, 20), value=values[3]),
        ]

    def _spawn_traps(self) -> list[ExplosiveTrap]:
        profile = settings.DIFFICULTY_PROFILES[self.difficulty]
        floor_trap_multiplier = 1.0 + (self.floor - 1) * 0.1
        trap_specs = self.layout["trap_positions"]
        return [
            ExplosiveTrap(
                pygame.Rect(trap_specs[0][0][0], trap_specs[0][0][1], 24, 24),
                damage=max(1, int(trap_specs[0][1] * profile["trap_multiplier"] * floor_trap_multiplier)),
            ),
            ExplosiveTrap(
                pygame.Rect(trap_specs[1][0][0], trap_specs[1][0][1], 24, 24),
                damage=max(1, int(trap_specs[1][1] * profile["trap_multiplier"] * floor_trap_multiplier)),
            ),
            ExplosiveTrap(
                pygame.Rect(trap_specs[2][0][0], trap_specs[2][0][1], 24, 24),
                damage=max(1, int(trap_specs[2][1] * profile["trap_multiplier"] * floor_trap_multiplier)),
            ),
        ]

    def _spawn_objective_zones(self) -> list[ObjectiveZone]:
        return [ObjectiveZone(name, rect.copy()) for name, rect in self.layout["zones"]]

    def _spawn_decorations(self) -> list[Decoration]:
        return [Decoration(item.rect.copy(), item.color, item.kind) for item in self.layout["decorations"]]

    def _validate_chamber_accessibility(self) -> None:
        """Verifica si el mini-jefe es accesible desde la posición inicial del jugador (60, 60).
        Si no es accesible, automáticamente abre pasajes para garantizar acceso."""
        
        # El mini-jefe siempre es el último enemigo en la lista
        if not self.layout["enemy_specs"]:
            return
        
        jefe_x, jefe_y, _, _ = self.layout["enemy_specs"][-1]
        jefe_pos = (jefe_x, jefe_y)
        
        # Verificar si el jefe es alcanzable
        if self._is_position_reachable((60, 60), jefe_pos):
            return  # El jefe es accesible, no hay nada que hacer
        
        # Si no es accesible, intentar abrir pasajes
        self._fix_sealed_chamber(jefe_pos)

    def _is_position_reachable(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        """Usa flood-fill para verificar si end_pos es alcanzable desde start_pos sin atravesar muros."""
        
        TILE_SIZE = 20
        GRID_WIDTH = 960 // TILE_SIZE
        GRID_HEIGHT = 640 // TILE_SIZE
        
        # Convertir posiciones a coordenadas de grilla (usando centro del jugador/jefe)
        start_tile = (int(start_pos[0] // TILE_SIZE), int(start_pos[1] // TILE_SIZE))
        end_tile = (int(end_pos[0] // TILE_SIZE), int(end_pos[1] // TILE_SIZE))
        
        # Crear grilla de tiles bloqueados
        blocked = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Marcar tiles bloqueados por muros
        for wall in self.walls:
            # Convertir rect del muro a tiles bloqueados
            tile_x1 = wall.left // TILE_SIZE
            tile_y1 = wall.top // TILE_SIZE
            tile_x2 = (wall.right - 1) // TILE_SIZE
            tile_y2 = (wall.bottom - 1) // TILE_SIZE
            
            for ty in range(max(0, tile_y1), min(GRID_HEIGHT, tile_y2 + 1)):
                for tx in range(max(0, tile_x1), min(GRID_WIDTH, tile_x2 + 1)):
                    blocked[ty][tx] = True
        
        # Flood-fill desde start_tile
        visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        queue = [start_tile]
        visited[start_tile[1]][start_tile[0]] = True
        
        while queue:
            tx, ty = queue.pop(0)
            
            # Si alcanzamos el tile del jefe, es alcanzable
            if (tx, ty) == end_tile:
                return True
            
            # Explorar vecinos (4 direcciones)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = tx + dx, ty + dy
                
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    if not visited[ny][nx] and not blocked[ny][nx]:
                        visited[ny][nx] = True
                        queue.append((nx, ny))
        
        return False

    def _fix_sealed_chamber(self, jefe_pos: tuple[int, int]) -> None:
        """Automáticamente abre pasajes removiendo muros para hacer accesible el jefe."""
        
        TILE_SIZE = 20
        jefe_tile = (int(jefe_pos[0] // TILE_SIZE), int(jefe_pos[1] // TILE_SIZE))
        
        # Encontrar muros que están bloqueando el acceso
        candidate_walls = []
        
        for i, wall in enumerate(self.walls):
            # Convertir wall rect a tiles
            wall_tiles = set()
            tile_x1 = wall.left // TILE_SIZE
            tile_y1 = wall.top // TILE_SIZE
            tile_x2 = (wall.right - 1) // TILE_SIZE
            tile_y2 = (wall.bottom - 1) // TILE_SIZE
            
            for ty in range(max(0, tile_y1), min(32, tile_y2 + 1)):
                for tx in range(max(0, tile_x1), min(48, tile_x2 + 1)):
                    wall_tiles.add((tx, ty))
            
            # Calcular distancia de este muro al jefe
            min_dist = min(
                abs(jefe_tile[0] - tx) + abs(jefe_tile[1] - ty)
                for tx, ty in wall_tiles
            )
            
            # Solo considerar muros cercanos al jefe (dentro de 5 tiles)
            if min_dist <= 5 and i > 0:  # No remover muros de borde
                candidate_walls.append((min_dist, i, wall))
        
        # Remover el muro más cercano
        if candidate_walls:
            candidate_walls.sort()
            _, wall_idx, wall_to_remove = candidate_walls[0]
            self.walls.pop(wall_idx)
            
            # Verificar si ahora es accesible; si no, remover otro muro
            if not self._is_position_reachable((60, 60), jefe_pos):
                self._fix_sealed_chamber(jefe_pos)  # Recursivamente abrir más pasajes
