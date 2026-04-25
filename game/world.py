"""Elementos del mundo: mapa, objetos y zonas."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

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


class World:
    def __init__(self) -> None:
        self.walls = self._build_walls()
        self.enemies = self._spawn_enemies()
        self.treasures = self._spawn_treasures()
        self.traps = self._spawn_traps()
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
        return [
            Enemy(120, 200, patrol_width=70, enemy_type="terrestre"),
            Enemy(520, 130, patrol_width=90, enemy_type="volador"),
            Enemy(720, 250, patrol_width=80, enemy_type="terrestre"),
            Enemy(330, 520, patrol_width=95, enemy_type="volador"),
            Enemy(760, 520, patrol_width=110, enemy_type="mini_jefe"),
        ]

    def _spawn_treasures(self) -> list[Treasure]:
        return [
            Treasure(pygame.Rect(90, 560, 20, 20), value=25),
            Treasure(pygame.Rect(390, 80, 20, 20), value=35),
            Treasure(pygame.Rect(875, 90, 20, 20), value=40),
            Treasure(pygame.Rect(705, 565, 20, 20), value=30),
        ]

    def _spawn_traps(self) -> list[ExplosiveTrap]:
        return [
            ExplosiveTrap(pygame.Rect(280, 200, 24, 24), damage=10),
            ExplosiveTrap(pygame.Rect(560, 430, 24, 24), damage=14),
            ExplosiveTrap(pygame.Rect(820, 300, 24, 24), damage=12),
        ]
