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
        self.walls = self._build_walls()
        self.decorations = self._spawn_decorations()
        self.enemies = self._spawn_enemies()
        self.treasures = self._spawn_treasures()
        self.traps = self._spawn_traps()
        self.objective_zones = self._spawn_objective_zones()
        self.shop_zone = pygame.Rect(780, 520, 130, 90)

    def _build_walls(self) -> list[pygame.Rect]:
        return [
            pygame.Rect(0, 0, 960, 20),
            pygame.Rect(0, 620, 960, 20),
            pygame.Rect(0, 0, 20, 640),
            pygame.Rect(940, 0, 20, 640),
            pygame.Rect(180, 120, 200, 20),
            pygame.Rect(440, 200, 20, 200),
            pygame.Rect(610, 110, 260, 20),
            pygame.Rect(250, 450, 250, 20),
            pygame.Rect(620, 350, 20, 190),
        ]

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
        enemy_specs = [
            (120, 200, 70, "terrestre"),
            (520, 130, 90, "volador"),
            (720, 250, 80, "terrestre"),
            (330, 520, 95, "volador"),
            (760, 520, 110, "mini_jefe"),
        ]

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
        return [
            Treasure(pygame.Rect(90, 560, 20, 20), value=values[0]),
            Treasure(pygame.Rect(390, 80, 20, 20), value=values[1]),
            Treasure(pygame.Rect(875, 90, 20, 20), value=values[2]),
            Treasure(pygame.Rect(705, 565, 20, 20), value=values[3]),
        ]

    def _spawn_traps(self) -> list[ExplosiveTrap]:
        profile = settings.DIFFICULTY_PROFILES[self.difficulty]
        floor_trap_multiplier = 1.0 + (self.floor - 1) * 0.1
        return [
            ExplosiveTrap(pygame.Rect(280, 200, 24, 24), damage=max(1, int(10 * profile["trap_multiplier"] * floor_trap_multiplier))),
            ExplosiveTrap(pygame.Rect(560, 430, 24, 24), damage=max(1, int(14 * profile["trap_multiplier"] * floor_trap_multiplier))),
            ExplosiveTrap(pygame.Rect(820, 300, 24, 24), damage=max(1, int(12 * profile["trap_multiplier"] * floor_trap_multiplier))),
        ]

    def _spawn_objective_zones(self) -> list[ObjectiveZone]:
        return [
            ObjectiveZone("Sector Norte", pygame.Rect(40, 40, 320, 200)),
            ObjectiveZone("Ruinas Centrales", pygame.Rect(380, 170, 250, 260)),
            ObjectiveZone("Santuario Sur", pygame.Rect(640, 430, 260, 170)),
        ]

    def _spawn_decorations(self) -> list[Decoration]:
        return [
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
        ]
