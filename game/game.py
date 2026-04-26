"""Bucle principal y logica de juego."""

from __future__ import annotations

import random

import pygame

from game import settings
from game.audio import AudioManager
from game.achievements import AchievementManager
from game.entities import Particle, Player, Projectile
from game.persistence import GameSave, load_game_save, save_game_save
from game.ui import UI
from game.world import World


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.window_size = (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        self.screen = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 28)

        self.ui = UI(self.font)
        self.audio = AudioManager()
        self.save_data = load_game_save()
        self.achievements = AchievementManager()
        self.achievements.from_dict(self.save_data.achievements)
        self.difficulty = "normal"
        self.reset()

    def reset(self) -> None:
        self.floor = 1
        self.player = Player(60, 60, speed=settings.PLAYER_SPEED)
        self._apply_save_data_to_player()
        self.projectiles: list[Projectile] = []
        self.particles: list[Particle] = []
        self.world = World(difficulty=self.difficulty, floor=self.floor)
        self.score = 0
        self.attack_cooldown = 0.0
        self.contact_damage_timer = 0.0
        self.pending_level_ups = 0
        self.level_up_options: list[dict[str, str]] = []
        self.message = ""
        self.game_over = False
        self.victory = False
        self.game_state = "title"
        self.previous_game_state = "title"
        self.active_zone_index = 0
        self.zone_completion_bonus = 20
        self.objective_score = self._floor_objective_score()
        self.active_zone_event = {}
        self.side_quest = {}
        self.frame_stats = {
            "enemies_defeated": 0,
            "treasures_collected": 0,
            "damage_taken": 0,
            "play_time": 0.0,
        }
        self._accumulated_time = 0.0
        self._session_saved = False
        self._no_damage_timer = 0.0
        self._achievement_notifications: list[tuple[str, str, str, float]] = []  # (icon, name, desc, time)
        self._roll_zone_event(first_event=True)
        self._generate_side_quest()

    def _apply_save_data_to_player(self) -> None:
        for weapon_key in self.save_data.unlocked_weapons:
            self.player.unlock_weapon(weapon_key)

        if self.player.has_weapon(self.save_data.active_weapon):
            self.player.set_active_weapon(self.save_data.active_weapon)

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            running = self._handle_events()

            if self.game_state == "playing" or self._level_up_menu_open():
                self._update(dt)

            self._update_achievement_notifications(dt)

            self._draw(dt)

        pygame.quit()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                width = max(640, event.w)
                height = max(360, event.h)
                self.window_size = (width, height)
                self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
                continue
            if event.type == pygame.KEYDOWN:
                if self.game_state == "title":
                    if event.key == pygame.K_1:
                        self.difficulty = "easy"
                    elif event.key == pygame.K_2:
                        self.difficulty = "normal"
                    elif event.key == pygame.K_3:
                        self.difficulty = "hard"
                    elif event.key == pygame.K_l:
                        self.previous_game_state = "title"
                        self.game_state = "achievements"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                        self.game_state = "playing"
                    if event.key == pygame.K_ESCAPE:
                        return False
                    continue

                if self.game_state == "achievements":
                    if event.key in (pygame.K_ESCAPE, pygame.K_l, pygame.K_RETURN):
                        self.game_state = self.previous_game_state
                    continue

                if self.game_state == "paused":
                    if event.key == pygame.K_p:
                        self.game_state = "playing"
                    if event.key == pygame.K_r:
                        self.reset()
                    if event.key == pygame.K_ESCAPE:
                        return False
                    continue

                if self.game_state in ("game_over", "victory"):
                    if event.key == pygame.K_r:
                        self.reset()
                    if event.key == pygame.K_RETURN:
                        self.reset()
                        self.game_state = "playing"
                    if event.key == pygame.K_ESCAPE:
                        return False
                    continue

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
                if event.key == pygame.K_p and self.game_state == "playing":
                    self.game_state = "paused"
                if event.key == pygame.K_e and not self.game_over and not self.victory:
                    self._try_shop_heal()

        return True

    def _update(self, dt: float) -> None:
        if self.game_state != "playing" and not self._level_up_menu_open():
            return

        self._accumulated_time += dt
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
        self._update_particles(dt)
        self._check_treasure_collisions()
        self._check_trap_collisions()
        self._check_enemy_collisions()
        self._check_objective_zones()
        self._check_game_state()

    def _player_attack(self) -> None:
        if self.attack_cooldown > 0:
            return

        weapon = self.player.get_active_weapon()
        self.attack_cooldown = weapon.cooldown
        damage_bonus = self.active_zone_event.get("player_damage_bonus", 0)
        mouse_x, mouse_y = self._window_to_game_coords(*pygame.mouse.get_pos())
        shot_direction = pygame.Vector2(
            mouse_x - self.player.rect.centerx,
            mouse_y - self.player.rect.centery,
        )
        if shot_direction.length_squared() == 0:
            shot_direction = self.player.facing
        else:
            shot_direction = shot_direction.normalize()

        self.player.facing = shot_direction
        self.projectiles.append(
            Projectile(
                x=self.player.rect.centerx,
                y=self.player.rect.centery,
                direction=shot_direction,
                weapon=weapon,
                damage=weapon.damage + self.player.stats.attack // 2 + damage_bonus,
            )
        )
        self.audio.play("shoot")
        self._spawn_burst(
            x=self.player.rect.centerx + int(shot_direction.x * 12),
            y=self.player.rect.centery + int(shot_direction.y * 12),
            color=weapon.color,
            count=5,
            speed_range=(40, 110),
            life_range=(0.12, 0.25),
            radius_range=(2, 3),
        )

    def _update_projectiles(self, dt: float) -> None:
        for projectile in self.projectiles[:]:
            projectile.update(dt)

            if self._projectile_hits_wall(projectile) or self._projectile_out_of_bounds(projectile):
                self.projectiles.remove(projectile)
                continue

            enemy_hit = self._find_enemy_hit_by_projectile(projectile)
            if enemy_hit is not None:
                impact_x = projectile.rect.centerx
                impact_y = projectile.rect.centery
                enemy_hit.take_damage(projectile.damage)
                self.audio.play("hit")
                self._spawn_burst(
                    x=impact_x,
                    y=impact_y,
                    color=settings.PARTICLE_HIT_COLOR,
                    count=8,
                    speed_range=(50, 160),
                    life_range=(0.15, 0.35),
                    radius_range=(2, 4),
                )
                if not enemy_hit.alive:
                    self.player.gold += 8
                    self._grant_xp(14)
                    self._on_enemy_defeated(enemy_hit)
                    self._spawn_burst(
                        x=enemy_hit.rect.centerx,
                        y=enemy_hit.rect.centery,
                        color=settings.PARTICLE_ZONE_COLOR,
                        count=14,
                        speed_range=(60, 190),
                        life_range=(0.2, 0.45),
                        radius_range=(2, 4),
                    )
                self.projectiles.remove(projectile)

    def _update_particles(self, dt: float) -> None:
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

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
            self.audio.play("pickup")
            self._spawn_burst(
                x=self.player.rect.centerx,
                y=self.player.rect.centery,
                color=settings.PARTICLE_PICKUP_COLOR,
                count=8,
                speed_range=(30, 120),
                life_range=(0.18, 0.4),
                radius_range=(2, 4),
            )
        elif self.player.rect.colliderect(self.world.shop_zone):
            self.message = "No tienes oro suficiente"

    def _check_treasure_collisions(self) -> None:
        for treasure in self.world.treasures:
            if not treasure.collected and self.player.rect.colliderect(treasure.rect):
                treasure.collected = True
                treasure_multiplier = self.active_zone_event.get("treasure_multiplier", 1.0)
                treasure_value = max(1, int(treasure.value * treasure_multiplier))
                self.player.gold += treasure_value
                self._grant_xp(10)
                self.score += treasure_value
                self.frame_stats["treasures_collected"] += 1
                
                # Trackear logros de tesoros
                self.achievements.increment_progress("treasure_hunter", 1)
                self.achievements.increment_progress("treasure_master", 1)
                self.achievements.increment_progress("rich", treasure_value)
                
                self.audio.play("pickup")
                self._spawn_burst(
                    x=treasure.rect.centerx,
                    y=treasure.rect.centery,
                    color=settings.PARTICLE_PICKUP_COLOR,
                    count=10,
                    speed_range=(40, 140),
                    life_range=(0.18, 0.45),
                    radius_range=(2, 4),
                )
                self._advance_side_quest("treasure")

    def _check_objective_zones(self) -> None:
        if self.active_zone_index >= len(self.world.objective_zones):
            return

        active_zone = self.world.objective_zones[self.active_zone_index]
        if active_zone.completed:
            return

        if not self.player.rect.colliderect(active_zone.rect):
            return

        zone_enemies = [enemy for enemy in self.world.enemies if enemy.rect.colliderect(active_zone.rect)]
        zone_treasures = [treasure for treasure in self.world.treasures if treasure.rect.colliderect(active_zone.rect)]

        enemies_cleared = all(not enemy.alive for enemy in zone_enemies)
        treasures_cleared = all(treasure.collected for treasure in zone_treasures)

        if enemies_cleared and treasures_cleared:
            active_zone.completed = True
            self.score += self.zone_completion_bonus
            self.player.gold += 10
            self._grant_xp(12)
            self.message = f"Zona completada: {active_zone.name}"
            self.active_zone_index += 1
            self.audio.play("pickup")
            self._spawn_burst(
                x=active_zone.rect.centerx,
                y=active_zone.rect.centery,
                color=settings.PARTICLE_ZONE_COLOR,
                count=16,
                speed_range=(50, 170),
                life_range=(0.22, 0.5),
                radius_range=(2, 5),
            )
            self._advance_side_quest("zone")
            self._roll_zone_event()

            if self.active_zone_index < len(self.world.objective_zones):
                self.level_up_options = self.level_up_options

    def _check_trap_collisions(self) -> None:
        for trap in self.world.traps:
            if not trap.triggered and self.player.rect.colliderect(trap.rect):
                trap.triggered = True
                self.player.take_damage(trap.damage)
                self.message = "Piso una trampa"
                self.audio.play("damage")
                self._spawn_burst(
                    x=trap.rect.centerx,
                    y=trap.rect.centery,
                    color=settings.PARTICLE_DAMAGE_COLOR,
                    count=10,
                    speed_range=(60, 180),
                    life_range=(0.15, 0.35),
                    radius_range=(2, 4),
                )

    def _check_enemy_collisions(self) -> None:
        if self.contact_damage_timer > 0:
            return

        for enemy in self.world.enemies:
            if enemy.alive and self.player.rect.colliderect(enemy.rect):
                attack_multiplier = self.active_zone_event.get("enemy_attack_multiplier", 1.0)
                self.player.take_damage(max(1, int(enemy.stats.attack * attack_multiplier)))
                self.frame_stats["damage_taken"] += 1
                self.audio.play("damage")
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
                self._spawn_burst(
                    x=self.player.rect.centerx,
                    y=self.player.rect.centery,
                    color=settings.PARTICLE_DAMAGE_COLOR,
                    count=12,
                    speed_range=(70, 210),
                    life_range=(0.16, 0.38),
                    radius_range=(2, 4),
                )
                break

    def _check_game_state(self) -> None:
        if self.player.hp <= 0:
            self.game_over = True
            self.game_state = "game_over"
            self.message = "Derrota. Presiona R para reiniciar"
            self._finalize_session(victory=False)
            return

        all_treasures_collected = all(t.collected for t in self.world.treasures)
        all_enemies_defeated = all(not e.alive for e in self.world.enemies)
        miniboss_defeated = any(e.enemy_type == "mini_jefe" and not e.alive for e in self.world.enemies)

        if (self.score >= self.objective_score and miniboss_defeated) or (all_treasures_collected and all_enemies_defeated):
            self._advance_dungeon_floor()

    def _update_achievement_notifications(self, dt: float) -> None:
        newly_unlocked = self.achievements.get_newly_unlocked()
        for achievement_id in newly_unlocked:
            achievement = self.achievements.achievements.get(achievement_id)
            if achievement is None:
                continue
            self._achievement_notifications.append((achievement.icon, achievement.name, achievement.description, 4.0))

        updated_notifications: list[tuple[str, str, str, float]] = []
        for icon, name, description, timer in self._achievement_notifications:
            timer -= dt
            if timer > 0:
                updated_notifications.append((icon, name, description, timer))
        self._achievement_notifications = updated_notifications

    def _achievement_ui_data(self) -> dict[str, dict[str, object]]:
        return {
            achievement_id: {
                "icon": achievement.icon,
                "name": achievement.name,
                "description": achievement.description,
                "unlocked": achievement.unlocked,
            }
            for achievement_id, achievement in self.achievements.achievements.items()
        }

    def _draw(self, dt: float) -> None:
        self.screen.fill(settings.BACKGROUND_COLOR)
        
        # Actualizar animaciones del UI
        if self.game_state in ("title", "achievements"):
            self.ui._update_title_animation(dt)

        self._draw_background_grid()

        for zone in self.world.objective_zones:
            self._draw_zone_backdrop(zone)

        for decoration in self.world.decorations:
            self._draw_decoration(decoration)

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

        for particle in self.particles:
            alpha_surface = pygame.Surface((particle.radius * 4, particle.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(
                alpha_surface,
                (*particle.color, max(20, int(255 * min(1.0, particle.life / 0.45)))),
                (particle.radius * 2, particle.radius * 2),
                particle.radius,
            )
            self.screen.blit(
                alpha_surface,
                (int(particle.position.x) - particle.radius * 2, int(particle.position.y) - particle.radius * 2),
            )

        if self._should_draw_player():
            pygame.draw.rect(self.screen, settings.PLAYER_COLOR, self.player.rect)

        if self.game_state in ("title", "achievements"):
            self.ui.draw_title_screen(
                self.screen,
                best_score=self.save_data.best_score,
                total_runs=self.save_data.total_runs,
                best_level=self.save_data.best_level,
                difficulty_label=settings.DIFFICULTY_PROFILES[self.difficulty]["label"],
                current_difficulty=self.difficulty,
            )
            if self.game_state == "achievements":
                self.ui.draw_achievements_menu(
                    self.screen,
                    achievements_data=self._achievement_ui_data(),
                    unlocked_count=self.achievements.get_unlocked_count(),
                    total_count=self.achievements.get_total_count(),
                )
        else:
            self.ui.draw_hud(
                self.screen,
                floor=self.floor,
                hp=self.player.hp,
                max_hp=self.player.stats.max_hp,
                level=self.player.level,
                xp=self.player.xp,
                gold=self.player.gold,
                score=self.score,
                objective_score=self.objective_score,
                active_weapon=self.player.get_active_weapon().name,
                unlocked_weapons=[self.player.weapons[key].name for key in self._weapon_keys() if self.player.has_weapon(key)],
                zone_name=self._current_zone_name(),
                zone_progress=self._zone_progress_text(),
                event_name=self.active_zone_event.get("label", "Sin evento"),
                event_description=self.active_zone_event.get("description", ""),
                quest_text=self._side_quest_text(),
            )
            self.ui.draw_minimap(
                self.screen,
                player_rect=self.player.rect,
                world_size=(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
                zones=self.world.objective_zones,
                enemies=self.world.enemies,
                shop_zone=self.world.shop_zone,
            )

            if self._level_up_menu_open():
                self.ui.draw_level_up_menu(
                    self.screen,
                    options=self.level_up_options,
                    pending_levels=self.pending_level_ups,
                )

            if self.game_state == "paused":
                self.ui.draw_pause_overlay(self.screen)

            if self.game_state in ("game_over", "victory"):
                self.ui.draw_end_screen(
                    self.screen,
                    victory=self.game_state == "victory",
                    score=self.score,
                    play_time=self._accumulated_time,
                    enemies_defeated=sum(1 for enemy in self.world.enemies if not enemy.alive),
                    treasures_collected=sum(1 for treasure in self.world.treasures if treasure.collected),
                    level=self.player.level,
                )

            if self.message and self.game_state == "playing":
                message_text = self.font.render(self.message, True, settings.TEXT_COLOR)
                self.screen.blit(message_text, (24, 146))

        if self._achievement_notifications and self.game_state != "achievements":
            icon, name, description, _ = self._achievement_notifications[0]
            self.ui.draw_achievement_notification(self.screen, icon, name, description)

        viewport = self._get_viewport_rect()
        self.window.fill((0, 0, 0))
        scaled_frame = pygame.transform.smoothscale(self.screen, viewport.size)
        self.window.blit(scaled_frame, viewport.topleft)
        pygame.display.flip()

    def _window_to_game_coords(self, window_x: int, window_y: int) -> tuple[int, int]:
        viewport = self._get_viewport_rect()
        relative_x = window_x - viewport.x
        relative_y = window_y - viewport.y
        clamped_x = min(max(relative_x, 0), max(0, viewport.width - 1))
        clamped_y = min(max(relative_y, 0), max(0, viewport.height - 1))
        scale_x = settings.SCREEN_WIDTH / max(1, viewport.width)
        scale_y = settings.SCREEN_HEIGHT / max(1, viewport.height)
        game_x = int(clamped_x * scale_x)
        game_y = int(clamped_y * scale_y)
        return game_x, game_y

    def _get_viewport_rect(self) -> pygame.Rect:
        base_w = settings.SCREEN_WIDTH
        base_h = settings.SCREEN_HEIGHT
        window_w, window_h = self.window_size
        if window_w <= 0 or window_h <= 0:
            return pygame.Rect(0, 0, base_w, base_h)

        scale = min(window_w / base_w, window_h / base_h)
        scaled_w = max(1, int(base_w * scale))
        scaled_h = max(1, int(base_h * scale))
        offset_x = (window_w - scaled_w) // 2
        offset_y = (window_h - scaled_h) // 2
        return pygame.Rect(offset_x, offset_y, scaled_w, scaled_h)

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

    def _draw_background_grid(self) -> None:
        grid_color = (28, 35, 44)
        step = 40
        for x in range(0, settings.SCREEN_WIDTH, step):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, settings.SCREEN_HEIGHT), 1)
        for y in range(0, settings.SCREEN_HEIGHT, step):
            pygame.draw.line(self.screen, grid_color, (0, y), (settings.SCREEN_WIDTH, y), 1)

    def _draw_zone_backdrop(self, zone) -> None:
        color = (34, 42, 54) if not zone.completed else (28, 52, 38)
        overlay = pygame.Surface((zone.rect.width, zone.rect.height), pygame.SRCALPHA)
        overlay.fill((*color, 60))
        self.screen.blit(overlay, zone.rect.topleft)

        border_color = (68, 88, 108) if not zone.completed else (96, 160, 120)
        pygame.draw.rect(self.screen, border_color, zone.rect, 2)

    def _draw_decoration(self, decoration) -> None:
        if decoration.kind == "pillar":
            pygame.draw.rect(self.screen, decoration.color, decoration.rect, border_radius=3)
            top = pygame.Rect(decoration.rect.x - 4, decoration.rect.y - 4, decoration.rect.width + 8, 8)
            pygame.draw.rect(self.screen, (96, 108, 124), top, border_radius=4)
        elif decoration.kind == "lamp":
            pygame.draw.circle(self.screen, decoration.color, decoration.rect.center, decoration.rect.width // 2)
            glow = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*decoration.color, 40), (20, 20), 16)
            self.screen.blit(glow, (decoration.rect.centerx - 20, decoration.rect.centery - 20))
        elif decoration.kind == "rune":
            pygame.draw.rect(self.screen, decoration.color, decoration.rect, border_radius=2)
            pygame.draw.line(self.screen, (130, 150, 180), decoration.rect.topleft, decoration.rect.bottomright, 1)
            pygame.draw.line(self.screen, (130, 150, 180), decoration.rect.topright, decoration.rect.bottomleft, 1)

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
            
            # Trackear logros de nivel
            self.achievements.increment_progress("level_5", levels_gained)
            self.achievements.increment_progress("level_10", levels_gained)
            
            self.audio.play("levelup")

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
            self.achievements.increment_progress("all_weapons", 1)
            self.message = "Desbloqueaste Rafaga"
        elif upgrade_key == "unlock_heavy":
            self.player.unlock_weapon("heavy")
            self.player.set_active_weapon("heavy")
            self.achievements.increment_progress("all_weapons", 1)
            self.message = "Desbloqueaste Canon"

        self.pending_level_ups = max(0, self.pending_level_ups - 1)
        if self.pending_level_ups > 0:
            self.level_up_options = self._build_level_up_options()
        else:
            self.level_up_options = []

    def _on_enemy_defeated(self, enemy) -> None:
        self.frame_stats["enemies_defeated"] += 1
        if enemy.enemy_type == "mini_jefe":
            self.score += 40
            self.achievements.unlock("miniboss_defeated")
        else:
            self.score += 25
        
        # Trackear logros de enemigos derrotados
        self.achievements.increment_progress("first_enemy", 1)
        self.achievements.increment_progress("slayer_10", 1)
        self.achievements.increment_progress("slayer_50", 1)
        
        self._advance_side_quest("enemy")

    def _finalize_session(self, victory: bool) -> None:
        if self._session_saved:
            return

        self._session_saved = True
        
        # Trackear logro de superviviente (sin daño por 5 minutos)
        if self.frame_stats["damage_taken"] == 0 and self._accumulated_time >= 300:
            self.achievements.unlock("survivor")
        
        self.save_data.total_runs += 1
        self.save_data.total_enemies_defeated += self.frame_stats["enemies_defeated"]
        self.save_data.total_treasures_collected += self.frame_stats["treasures_collected"]
        self.save_data.total_damage_taken += self.frame_stats["damage_taken"]
        self.save_data.best_score = max(self.save_data.best_score, self.score)
        self.save_data.best_level = max(self.save_data.best_level, self.player.level)
        self.save_data.active_weapon = self.player.active_weapon_key
        self.save_data.unlocked_weapons = sorted(self.player.unlocked_weapons)
        self.save_data.achievements = self.achievements.to_dict()
        save_game_save(self.save_data)

    def _roll_zone_event(self, first_event: bool = False) -> None:
        events = [
            {
                "key": "fortune",
                "label": "Fortuna",
                "description": "Los tesoros valen mas en esta zona.",
                "treasure_multiplier": 1.35,
                "enemy_attack_multiplier": 1.0,
                "player_damage_bonus": 0,
            },
            {
                "key": "frenesi",
                "label": "Frenesi",
                "description": "Los enemigos atacan con mas fuerza.",
                "treasure_multiplier": 1.0,
                "enemy_attack_multiplier": 1.18,
                "player_damage_bonus": 0,
            },
            {
                "key": "bendicion",
                "label": "Bendicion",
                "description": "Tus disparos ganan poder adicional.",
                "treasure_multiplier": 1.0,
                "enemy_attack_multiplier": 1.0,
                "player_damage_bonus": 2,
            },
        ]

        self.active_zone_event = random.choice(events)

        if first_event:
            self.message = f"Evento activo: {self.active_zone_event['label']}"

    def _generate_side_quest(self) -> None:
        quests = [
            {"key": "enemy", "label": "Derrota enemigos", "target": random.randint(3, 5), "reward_gold": 18, "reward_score": 20},
            {"key": "treasure", "label": "Recoge tesoros", "target": random.randint(2, 4), "reward_gold": 20, "reward_score": 24},
            {"key": "zone", "label": "Explora zonas", "target": 1, "reward_gold": 25, "reward_score": 30},
        ]
        self.side_quest = random.choice(quests)
        self.side_quest["progress"] = 0
        self.side_quest["completed"] = False

    def _advance_side_quest(self, quest_key: str, amount: int = 1) -> None:
        if not self.side_quest or self.side_quest.get("completed"):
            return

        if self.side_quest.get("key") != quest_key:
            return

        self.side_quest["progress"] += amount
        if self.side_quest["progress"] >= self.side_quest["target"]:
            self.side_quest["completed"] = True
            self.player.gold += self.side_quest["reward_gold"]
            self.score += self.side_quest["reward_score"]
            self._grant_xp(10)
            self.audio.play("pickup")
            self._spawn_burst(
                x=self.player.rect.centerx,
                y=self.player.rect.centery,
                color=settings.PARTICLE_PICKUP_COLOR,
                count=12,
                speed_range=(40, 160),
                life_range=(0.18, 0.4),
                radius_range=(2, 4),
            )
            self.message = f"Mision completada: {self.side_quest['label']}"
            self._generate_side_quest()

    def _side_quest_text(self) -> str:
        if not self.side_quest:
            return "Sin mision activa"

        progress = self.side_quest.get("progress", 0)
        target = self.side_quest.get("target", 0)
        label = self.side_quest.get("label", "Mision")
        return f"Mision: {label} {progress}/{target}"

    def _spawn_burst(
        self,
        x: int,
        y: int,
        color: tuple[int, int, int],
        count: int,
        speed_range: tuple[int, int],
        life_range: tuple[float, float],
        radius_range: tuple[int, int],
    ) -> None:
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(speed_range[0], speed_range[1])
            direction = pygame.Vector2(1, 0).rotate(angle)
            velocity = direction * speed
            life = random.uniform(life_range[0], life_range[1])
            radius = random.randint(radius_range[0], radius_range[1])
            self.particles.append(
                Particle(
                    position=pygame.Vector2(float(x), float(y)),
                    velocity=velocity,
                    life=life,
                    color=color,
                    radius=radius,
                )
            )

    def _set_weapon_by_index(self, index: int) -> None:
        weapon_keys = self._weapon_keys()
        if index >= len(weapon_keys):
            return

        weapon_key = weapon_keys[index]
        if self.player.set_active_weapon(weapon_key):
            self.message = f"Arma activa: {self.player.get_active_weapon().name}"

    def _weapon_keys(self) -> list[str]:
        return ["basic", "rapid", "heavy"]

    def _current_zone_name(self) -> str:
        if self.active_zone_index >= len(self.world.objective_zones):
            return "Todas las zonas completas"

        return self.world.objective_zones[self.active_zone_index].name

    def _zone_progress_text(self) -> str:
        total_zones = len(self.world.objective_zones)
        if self.active_zone_index >= len(self.world.objective_zones):
            return f"Progreso: {total_zones}/{total_zones}"

        completed = sum(1 for zone in self.world.objective_zones if zone.completed)
        return f"Progreso: {completed}/{total_zones}"

    def _floor_objective_score(self) -> int:
        base_score = settings.DIFFICULTY_PROFILES[self.difficulty]["objective_score"]
        multiplier = 1.0 + (self.floor - 1) * 0.22
        return int(base_score * multiplier)

    def _advance_dungeon_floor(self) -> None:
        previous_floor = self.floor
        self.floor += 1
        self.objective_score = self._floor_objective_score()
        self.world = World(difficulty=self.difficulty, floor=self.floor)
        self.player.rect.topleft = (60, 60)
        self.player.hp = min(self.player.stats.max_hp, self.player.hp + 22)
        self.active_zone_index = 0
        self.contact_damage_timer = 0.0
        self.attack_cooldown = 0.0
        self.projectiles.clear()
        self.particles.clear()
        self._roll_zone_event(first_event=True)
        self._generate_side_quest()

        if previous_floor == 1:
            self.achievements.unlock("first_victory")
            if self.difficulty == "hard":
                self.achievements.unlock("hard_mode")
            if self._accumulated_time < 180:
                self.achievements.unlock("speed_run")

        self.audio.play("victory")
        self.message = f"Descendiste al piso {self.floor}. Los enemigos son mas fuertes."
        self._spawn_burst(
            x=self.player.rect.centerx,
            y=self.player.rect.centery,
            color=settings.PARTICLE_ZONE_COLOR,
            count=24,
            speed_range=(70, 220),
            life_range=(0.2, 0.5),
            radius_range=(2, 5),
        )
