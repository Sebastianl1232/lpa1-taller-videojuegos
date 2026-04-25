"""Entidades principales del juego."""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Stats:
    max_hp: int
    attack: int
    defense: int


class Player:
    def __init__(self, x: int, y: int, speed: int) -> None:
        self.rect = pygame.Rect(x, y, 34, 34)
        self.speed = speed
        self.facing = pygame.Vector2(1, 0)
        self.stats = Stats(max_hp=100, attack=12, defense=4)
        self.hp = self.stats.max_hp
        self.level = 1
        self.xp = 0
        self.gold = 0

    def move(self, direction: pygame.Vector2, dt: float, walls: list[pygame.Rect]) -> None:
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.facing = direction

        self.rect.x += int(direction.x * self.speed * dt)
        self._resolve_collisions(walls, axis="x")

        self.rect.y += int(direction.y * self.speed * dt)
        self._resolve_collisions(walls, axis="y")

    def _resolve_collisions(self, walls: list[pygame.Rect], axis: str) -> None:
        for wall in walls:
            if self.rect.colliderect(wall):
                if axis == "x":
                    if self.rect.centerx < wall.centerx:
                        self.rect.right = wall.left
                    else:
                        self.rect.left = wall.right
                else:
                    if self.rect.centery < wall.centery:
                        self.rect.bottom = wall.top
                    else:
                        self.rect.top = wall.bottom

    def take_damage(self, raw_damage: int) -> int:
        damage = max(1, raw_damage - self.stats.defense)
        self.hp = max(0, self.hp - damage)
        return damage

    def apply_knockback(self, direction: pygame.Vector2, distance: float, walls: list[pygame.Rect]) -> None:
        if direction.length_squared() == 0:
            return

        force = direction.normalize() * distance
        self.rect.x += int(force.x)
        self._resolve_collisions(walls, axis="x")
        self.rect.y += int(force.y)
        self._resolve_collisions(walls, axis="y")

    def gain_xp(self, amount: int) -> None:
        self.xp += amount
        while self.xp >= self.level * 30:
            self.xp -= self.level * 30
            self.level += 1
            self.stats.max_hp += 8
            self.stats.attack += 2
            self.stats.defense += 1
            self.hp = min(self.stats.max_hp, self.hp + 12)


class Projectile:
    def __init__(self, x: int, y: int, direction: pygame.Vector2, speed: int) -> None:
        self.rect = pygame.Rect(x - 5, y - 5, 10, 10)
        self.position = pygame.Vector2(float(self.rect.x), float(self.rect.y))
        self.direction = direction.normalize() if direction.length_squared() > 0 else pygame.Vector2(1, 0)
        self.speed = speed

    def update(self, dt: float) -> None:
        self.position += self.direction * self.speed * dt
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)


class Enemy:
    def __init__(self, x: int, y: int, patrol_width: int, enemy_type: str = "terrestre") -> None:
        self.rect = pygame.Rect(x, y, 30, 30)
        self.enemy_type = enemy_type
        self.stats = Stats(max_hp=36 if enemy_type == "volador" else 44, attack=11, defense=2)
        self.hp = self.stats.max_hp
        self.speed = 135 if enemy_type == "volador" else 110
        self.direction = 1
        self.left_bound = x - patrol_width
        self.right_bound = x + patrol_width
        self.alive = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return

        self.rect.x += int(self.direction * self.speed * dt)
        if self.rect.left <= self.left_bound:
            self.rect.left = self.left_bound
            self.direction = 1
        elif self.rect.right >= self.right_bound:
            self.rect.right = self.right_bound
            self.direction = -1

    def take_damage(self, raw_damage: int) -> int:
        if not self.alive:
            return 0

        damage = max(1, raw_damage - self.stats.defense)
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.alive = False
        return damage
