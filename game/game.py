"""Bucle principal y logica de juego."""

from __future__ import annotations

import random

import pygame

from game import settings
from game.entities import Player, Projectile
from game.ui import UI
from game.world import World


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 28)

        self.ui = UI(self.font)
        self.reset()

    def reset(self) -> None:
        self.player = Player(60, 60, speed=settings.PLAYER_SPEED)
        self.projectiles: list[Projectile] = []
        self.world = World()
        self.score = 0
        self.attack_cooldown = 0.0
        self.contact_damage_timer = 0.0
        self.pending_level_ups = 0
        self.level_up_options: list[dict[str, str]] = []
        self.message = ""
        self.game_over = False
        self.victory = False

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            running = self._handle_events()

            if not self.game_over and not self.victory:
                self._update(dt)

            self._draw()

        pygame.quit()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self._level_up_menu_open():
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        self._apply_upgrade_choice(0)
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self._apply_upgrade_choice(1)
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self._apply_upgrade_choice(2)
                    continue

                if event.key == pygame.K_SPACE and not self.game_over and not self.victory:
                    self._player_attack()
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self._set_weapon_by_index(0)
                if event.key in (pygame.K_2, pygame.K_KP2):
                    self._set_weapon_by_index(1)
                if event.key in (pygame.K_3, pygame.K_KP3):
                    self._set_weapon_by_index(2)
                if event.key == pygame.K_e and not self.game_over and not self.victory:
                    self._try_shop_heal()
                if event.key == pygame.K_r and (self.game_over or self.victory):
                    self.reset()

        return True

    def _update(self, dt: float) -> None:
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.contact_damage_timer = max(0.0, self.contact_damage_timer - dt)

        if self._level_up_menu_open():
            return

        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            (1 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0)
            - (1 if keys[pygame.K_a] or keys[pygame.K_LEFT] else 0),
            (1 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0)
            - (1 if keys[pygame.K_w] or keys[pygame.K_UP] else 0),
        )
        self.player.move(direction, dt, self.world.walls)

        for enemy in self.world.enemies:
            enemy.update(dt, self.player.rect, self.world.walls)

        self._update_projectiles(dt)
        self._check_treasure_collisions()
        self._check_trap_collisions()
        self._check_enemy_collisions()
        self._check_game_state()

    def _player_attack(self) -> None:
        if self.attack_cooldown > 0:
            return

        weapon = self.player.get_active_weapon()
        self.attack_cooldown = weapon.cooldown
        self.projectiles.append(
            Projectile(
                x=self.player.rect.centerx,
                y=self.player.rect.centery,
                direction=self.player.facing,
                weapon=weapon,
                damage=weapon.damage + self.player.stats.attack // 2,
            )
        )

    def _update_projectiles(self, dt: float) -> None:
        for projectile in self.projectiles[:]:
            projectile.update(dt)

            if self._projectile_hits_wall(projectile) or self._projectile_out_of_bounds(projectile):
                self.projectiles.remove(projectile)
                continue

            enemy_hit = self._find_enemy_hit_by_projectile(projectile)
            if enemy_hit is not None:
                enemy_hit.take_damage(projectile.damage)
                if not enemy_hit.alive:
                    self.player.gold += 8
                    self._grant_xp(14)
                    self.score += 25
                self.projectiles.remove(projectile)

    def _projectile_hits_wall(self, projectile: Projectile) -> bool:
        return any(projectile.rect.colliderect(wall) for wall in self.world.walls)

    def _projectile_out_of_bounds(self, projectile: Projectile) -> bool:
        return not self.screen.get_rect().colliderect(projectile.rect)

    def _find_enemy_hit_by_projectile(self, projectile: Projectile):
        for enemy in self.world.enemies:
            if enemy.alive and projectile.rect.colliderect(enemy.rect):
                return enemy
        return None

    def _try_shop_heal(self) -> None:
        if self.player.rect.colliderect(self.world.shop_zone) and self.player.gold >= 15:
            self.player.gold -= 15
            self.player.hp = min(self.player.stats.max_hp, self.player.hp + 20)
            self.message = "Compraste una curacion"
        elif self.player.rect.colliderect(self.world.shop_zone):
            self.message = "No tienes oro suficiente"

    def _check_treasure_collisions(self) -> None:
        for treasure in self.world.treasures:
            if not treasure.collected and self.player.rect.colliderect(treasure.rect):
                treasure.collected = True
                self.player.gold += treasure.value
                self._grant_xp(10)
                self.score += treasure.value

    def _check_trap_collisions(self) -> None:
        for trap in self.world.traps:
            if not trap.triggered and self.player.rect.colliderect(trap.rect):
                trap.triggered = True
                self.player.take_damage(trap.damage)
                self.message = "Piso una trampa"

    def _check_enemy_collisions(self) -> None:
        if self.contact_damage_timer > 0:
            return

        for enemy in self.world.enemies:
            if enemy.alive and self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(enemy.stats.attack)
                knockback_direction = pygame.Vector2(
                    self.player.rect.centerx - enemy.rect.centerx,
                    self.player.rect.centery - enemy.rect.centery,
                )
                if knockback_direction.length_squared() == 0:
                    knockback_direction = pygame.Vector2(-enemy.direction, 0)

                self.player.apply_knockback(
                    direction=knockback_direction,
                    distance=settings.KNOCKBACK_DISTANCE,
                    walls=self.world.walls,
                )
                self.contact_damage_timer = settings.CONTACT_INVULN_TIME
                self.message = "Recibiste dano"
                break

    def _check_game_state(self) -> None:
        if self.player.hp <= 0:
            self.game_over = True
            self.message = "Derrota. Presiona R para reiniciar"
            return

        all_treasures_collected = all(t.collected for t in self.world.treasures)
        all_enemies_defeated = all(not e.alive for e in self.world.enemies)
        miniboss_defeated = any(e.enemy_type == "mini_jefe" and not e.alive for e in self.world.enemies)

        if (self.score >= settings.OBJECTIVE_SCORE and miniboss_defeated) or (all_treasures_collected and all_enemies_defeated):
            self.victory = True
            self.message = "Victoria. Presiona R para jugar otra vez"

    def _draw(self) -> None:
        self.screen.fill(settings.BACKGROUND_COLOR)

        for wall in self.world.walls:
            pygame.draw.rect(self.screen, settings.WALL_COLOR, wall)

        pygame.draw.rect(self.screen, settings.SHOP_COLOR, self.world.shop_zone)

        for treasure in self.world.treasures:
            if not treasure.collected:
                pygame.draw.rect(self.screen, settings.TREASURE_COLOR, treasure.rect)

        for trap in self.world.traps:
            color = (70, 70, 70) if trap.triggered else settings.TRAP_COLOR
            pygame.draw.rect(self.screen, color, trap.rect)

        for enemy in self.world.enemies:
            if enemy.alive:
                color = settings.BOSS_COLOR if enemy.enemy_type == "mini_jefe" else settings.ENEMY_COLOR
                pygame.draw.rect(self.screen, color, enemy.rect)
                self._draw_enemy_health_bar(enemy)

        for projectile in self.projectiles:
            pygame.draw.rect(self.screen, projectile.color, projectile.rect)

        if self._should_draw_player():
            pygame.draw.rect(self.screen, settings.PLAYER_COLOR, self.player.rect)

        self.ui.draw_hud(
            self.screen,
            hp=self.player.hp,
            max_hp=self.player.stats.max_hp,
            level=self.player.level,
            xp=self.player.xp,
            gold=self.player.gold,
            score=self.score,
            active_weapon=self.player.get_active_weapon().name,
            unlocked_weapons=[self.player.weapons[key].name for key in self._weapon_keys() if self.player.has_weapon(key)],
        )

        if self._level_up_menu_open():
            self.ui.draw_level_up_menu(
                self.screen,
                options=self.level_up_options,
                pending_levels=self.pending_level_ups,
            )

        if self.message:
            message_text = self.font.render(self.message, True, settings.TEXT_COLOR)
            self.screen.blit(message_text, (24, 146))

        if self.game_over or self.victory:
            self.ui.draw_center_message(self.screen, self.message)

        pygame.display.flip()

    def _draw_enemy_health_bar(self, enemy) -> None:
        bar_width = enemy.rect.width
        bar_height = 5
        bar_x = enemy.rect.x
        bar_y = enemy.rect.y - 10

        health_ratio = enemy.hp / enemy.stats.max_hp if enemy.stats.max_hp > 0 else 0
        current_width = int(bar_width * health_ratio)

        pygame.draw.rect(
            self.screen,
            settings.ENEMY_HP_BG_COLOR,
            pygame.Rect(bar_x, bar_y, bar_width, bar_height),
        )
        pygame.draw.rect(
            self.screen,
            settings.ENEMY_HP_COLOR,
            pygame.Rect(bar_x, bar_y, current_width, bar_height),
        )

    def _should_draw_player(self) -> bool:
        if self.contact_damage_timer <= 0:
            return True

        blink_phase = (pygame.time.get_ticks() // settings.PLAYER_BLINK_INTERVAL_MS) % 2
        return blink_phase == 0

    def _grant_xp(self, amount: int) -> None:
        levels_gained = self.player.gain_xp(amount)
        if levels_gained > 0:
            self.pending_level_ups += levels_gained
            if not self.level_up_options:
                self.level_up_options = self._build_level_up_options()

    def _level_up_menu_open(self) -> bool:
        return self.pending_level_ups > 0 and len(self.level_up_options) > 0

    def _build_level_up_options(self) -> list[dict[str, str]]:
        options: list[dict[str, str]] = [
            {
                "key": "hp",
                "title": "Vitalidad +20",
                "description": "Aumenta la vida maxima y recupera 20 HP.",
            },
            {
                "key": "attack",
                "title": "Ataque +2",
                "description": "Tus disparos ganan mas poder.",
            },
            {
                "key": "defense",
                "title": "Defensa +1",
                "description": "Recibes menos dano al chocar.",
            },
        ]

        if not self.player.has_weapon("rapid"):
            options.append(
                {
                    "key": "unlock_rapid",
                    "title": "Desbloquear Rafaga",
                    "description": "Arma rapida con baja cadencia y poco dano.",
                }
            )

        if not self.player.has_weapon("heavy"):
            options.append(
                {
                    "key": "unlock_heavy",
                    "title": "Desbloquear Canon",
                    "description": "Arma lenta pero devastadora.",
                }
            )

        if len(options) > 3:
            return random.sample(options, 3)

        return options[:3]

    def _apply_upgrade_choice(self, index: int) -> None:
        if index >= len(self.level_up_options):
            return

        choice = self.level_up_options[index]
        upgrade_key = choice["key"]

        if upgrade_key == "hp":
            self.player.boost_max_hp(20, heal_amount=20)
            self.message = "Mejora elegida: Vitalidad"
        elif upgrade_key == "attack":
            self.player.boost_attack(2)
            self.message = "Mejora elegida: Ataque"
        elif upgrade_key == "defense":
            self.player.boost_defense(1)
            self.message = "Mejora elegida: Defensa"
        elif upgrade_key == "unlock_rapid":
            self.player.unlock_weapon("rapid")
            self.player.set_active_weapon("rapid")
            self.message = "Desbloqueaste Rafaga"
        elif upgrade_key == "unlock_heavy":
            self.player.unlock_weapon("heavy")
            self.player.set_active_weapon("heavy")
            self.message = "Desbloqueaste Canon"

        self.pending_level_ups = max(0, self.pending_level_ups - 1)
        if self.pending_level_ups > 0:
            self.level_up_options = self._build_level_up_options()
        else:
            self.level_up_options = []

    def _set_weapon_by_index(self, index: int) -> None:
        weapon_keys = self._weapon_keys()
        if index >= len(weapon_keys):
            return

        weapon_key = weapon_keys[index]
        if self.player.set_active_weapon(weapon_key):
            self.message = f"Arma activa: {self.player.get_active_weapon().name}"

    def _weapon_keys(self) -> list[str]:
        return ["basic", "rapid", "heavy"]
