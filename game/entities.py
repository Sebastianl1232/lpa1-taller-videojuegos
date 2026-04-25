"""Entidades principales del juego."""

from __future__ import annotations

from dataclasses import dataclass
import math

import pygame

from game import settings


@dataclass
class Stats:
    max_hp: int
    attack: int
    defense: int


@dataclass(frozen=True)
class WeaponProfile:
    key: str
    name: str
    damage: int
    cooldown: float
    speed: int
    projectile_size: int
    color: tuple[int, int, int]


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    life: float
    color: tuple[int, int, int]
    radius: int

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.life -= dt

    def is_alive(self) -> bool:
        return self.life > 0


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
        self.weapons = {
            "basic": WeaponProfile(
                key="basic",
                name="Blaster",
                damage=8,
                cooldown=0.24,
                speed=420,
                projectile_size=10,
                color=(153, 229, 255),
            ),
            "rapid": WeaponProfile(
                key="rapid",
                name="Rafaga",
                damage=6,
                cooldown=0.11,
                speed=520,
                projectile_size=8,
                color=(120, 255, 200),
            ),
            "heavy": WeaponProfile(
                key="heavy",
                name="Canon",
                damage=18,
                cooldown=0.5,
                speed=320,
                projectile_size=16,
                color=(255, 176, 96),
            ),
        }
        self.unlocked_weapons = {"basic"}
        self.active_weapon_key = "basic"

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

    def gain_xp(self, amount: int) -> int:
        self.xp += amount
        levels_gained = 0
        while self.xp >= self.level * 30:
            self.xp -= self.level * 30
            self.level += 1
            levels_gained += 1

        return levels_gained

    def boost_max_hp(self, amount: int, heal_amount: int | None = None) -> None:
        self.stats.max_hp += amount
        self.hp = min(self.stats.max_hp, self.hp + (heal_amount if heal_amount is not None else amount))

    def boost_attack(self, amount: int) -> None:
        self.stats.attack += amount

    def boost_defense(self, amount: int) -> None:
        self.stats.defense += amount

    def unlock_weapon(self, weapon_key: str) -> bool:
        if weapon_key not in self.weapons:
            return False

        self.unlocked_weapons.add(weapon_key)
        return True

    def has_weapon(self, weapon_key: str) -> bool:
        return weapon_key in self.unlocked_weapons

    def set_active_weapon(self, weapon_key: str) -> bool:
        if weapon_key not in self.unlocked_weapons:
            return False

        self.active_weapon_key = weapon_key
        return True

    def get_active_weapon(self) -> WeaponProfile:
        return self.weapons[self.active_weapon_key]


class Projectile:
    def __init__(self, x: int, y: int, direction: pygame.Vector2, weapon: WeaponProfile, damage: int) -> None:
        size = weapon.projectile_size
        self.rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        self.position = pygame.Vector2(float(self.rect.x), float(self.rect.y))
        self.direction = direction.normalize() if direction.length_squared() > 0 else pygame.Vector2(1, 0)
        self.speed = weapon.speed
        self.color = weapon.color
        self.damage = damage

    def update(self, dt: float) -> None:
        self.position += self.direction * self.speed * dt
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)


class Enemy:
    def __init__(self, x: int, y: int, patrol_width: int, enemy_type: str = "terrestre", difficulty_profile: dict | None = None) -> None:
        difficulty_profile = difficulty_profile or settings.DIFFICULTY_PROFILES["normal"]
        self.enemy_type = enemy_type
        if enemy_type == "mini_jefe":
            self.rect = pygame.Rect(x, y, 46, 46)
            self.stats = Stats(max_hp=max(1, int(130 * difficulty_profile["enemy_hp_multiplier"])), attack=max(1, int(17 * difficulty_profile["enemy_attack_multiplier"])), defense=4)
            self.speed = int(135 * difficulty_profile["enemy_speed_multiplier"])
            self.chase_range = settings.BOSS_CHASE_RANGE
            self.burst_cooldown = 2.8
            self.burst_timer = 0.0
        elif enemy_type == "volador":
            self.rect = pygame.Rect(x, y, 30, 30)
            self.stats = Stats(max_hp=max(1, int(36 * difficulty_profile["enemy_hp_multiplier"])), attack=max(1, int(10 * difficulty_profile["enemy_attack_multiplier"])), defense=2)
            self.speed = int(145 * difficulty_profile["enemy_speed_multiplier"])
            self.chase_range = settings.FLYING_CHASE_RANGE
            self.bob_phase = 0.0
        else:
            self.rect = pygame.Rect(x, y, 30, 30)
            self.stats = Stats(max_hp=max(1, int(44 * difficulty_profile["enemy_hp_multiplier"])), attack=max(1, int(11 * difficulty_profile["enemy_attack_multiplier"])), defense=2)
            self.speed = int(110 * difficulty_profile["enemy_speed_multiplier"])
            self.chase_range = settings.GROUND_CHASE_RANGE

        self.hp = self.stats.max_hp
        self.direction = 1
        self.left_bound = x - patrol_width
        self.right_bound = x + patrol_width
        self.alive = True
        self.origin = pygame.Vector2(float(x), float(y))

    def update(self, dt: float, player_rect: pygame.Rect, walls: list[pygame.Rect]) -> None:
        if not self.alive:
            return

        to_player = pygame.Vector2(
            player_rect.centerx - self.rect.centerx,
            player_rect.centery - self.rect.centery,
        )
        distance = to_player.length()

        if self.enemy_type == "volador":
            self._update_flying(dt, to_player, distance)
            return

        if self.enemy_type == "mini_jefe":
            self._update_miniboss(dt, to_player, distance, walls)
            return

        self._update_ground(dt, to_player, distance, walls)

    def _update_ground(
        self,
        dt: float,
        to_player: pygame.Vector2,
        distance: float,
        walls: list[pygame.Rect],
    ) -> None:
        if distance <= self.chase_range and to_player.length_squared() > 0:
            move = to_player.normalize() * self.speed * dt
            self._move_with_collisions(move, walls)
        else:
            self.rect.x += int(self.direction * self.speed * dt)
            if self.rect.left <= self.left_bound:
                self.rect.left = self.left_bound
                self.direction = 1
            elif self.rect.right >= self.right_bound:
                self.rect.right = self.right_bound
                self.direction = -1
            self._resolve_collisions(walls, axis="x")

    def _update_flying(self, dt: float, to_player: pygame.Vector2, distance: float) -> None:
        move = pygame.Vector2(0, 0)
        if distance <= self.chase_range and to_player.length_squared() > 0:
            move = to_player.normalize() * self.speed * dt
        else:
            self.rect.x += int(self.direction * self.speed * dt * 0.7)
            if self.rect.left <= self.left_bound:
                self.rect.left = self.left_bound
                self.direction = 1
            elif self.rect.right >= self.right_bound:
                self.rect.right = self.right_bound
                self.direction = -1

        self.origin.y += move.y
        self.rect.x += int(move.x)
        self.bob_phase += dt * 5.0
        bob = math.sin(self.bob_phase) * 2
        self.rect.y = int(self.origin.y + bob)

    def _update_miniboss(
        self,
        dt: float,
        to_player: pygame.Vector2,
        distance: float,
        walls: list[pygame.Rect],
    ) -> None:
        self.burst_cooldown = max(0.0, self.burst_cooldown - dt)
        self.burst_timer = max(0.0, self.burst_timer - dt)

        if distance <= self.chase_range and to_player.length_squared() > 0:
            if self.burst_cooldown == 0:
                self.burst_timer = 0.8
                self.burst_cooldown = 3.0

            speed_multiplier = 1.9 if self.burst_timer > 0 else 1.15
            move = to_player.normalize() * self.speed * speed_multiplier * dt
            self._move_with_collisions(move, walls)
        else:
            self.rect.x += int(self.direction * self.speed * 0.55 * dt)
            if self.rect.left <= self.left_bound:
                self.rect.left = self.left_bound
                self.direction = 1
            elif self.rect.right >= self.right_bound:
                self.rect.right = self.right_bound
                self.direction = -1
            self._resolve_collisions(walls, axis="x")

    def _move_with_collisions(self, move: pygame.Vector2, walls: list[pygame.Rect]) -> None:
        self.rect.x += int(move.x)
        self._resolve_collisions(walls, axis="x")
        self.rect.y += int(move.y)
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
        if not self.alive:
            return 0

        damage = max(1, raw_damage - self.stats.defense)
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.alive = False
        return damage
