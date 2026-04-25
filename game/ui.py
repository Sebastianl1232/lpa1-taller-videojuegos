"""Render de HUD y textos de estado."""

from __future__ import annotations

import pygame

from game import settings


class UI:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.small_font = pygame.font.SysFont("consolas", 20)

    def draw_hud(
        self,
        surface: pygame.Surface,
        hp: int,
        max_hp: int,
        level: int,
        xp: int,
        gold: int,
        score: int,
        active_weapon: str,
        unlocked_weapons: list[str],
        zone_name: str,
        zone_progress: str,
        event_name: str,
        event_description: str,
        quest_text: str,
    ) -> None:
        hp_text = self.font.render(f"HP: {hp}/{max_hp}", True, settings.TEXT_COLOR)
        level_text = self.font.render(f"Nivel: {level}  XP: {xp}", True, settings.TEXT_COLOR)
        gold_text = self.font.render(f"Oro: {gold}", True, settings.TEXT_COLOR)
        score_text = self.font.render(f"Puntaje: {score}/{settings.OBJECTIVE_SCORE}", True, settings.TEXT_COLOR)
        weapon_text = self.font.render(f"Arma: {active_weapon}", True, settings.TEXT_COLOR)
        zone_text = self.small_font.render(f"Objetivo: {zone_name}", True, settings.TEXT_COLOR)
        progress_text = self.small_font.render(zone_progress, True, settings.TEXT_COLOR)
        event_text = self.small_font.render(f"Evento: {event_name}", True, settings.TEXT_COLOR)
        event_desc_text = self.small_font.render(event_description, True, settings.TEXT_COLOR)
        quest_text_surface = self.small_font.render(quest_text, True, settings.TEXT_COLOR)

        surface.blit(hp_text, (24, 20))
        surface.blit(level_text, (24, 50))
        surface.blit(gold_text, (24, 80))
        surface.blit(score_text, (24, 110))
        surface.blit(weapon_text, (24, 140))
        surface.blit(zone_text, (24, 180))
        surface.blit(progress_text, (24, 205))
        surface.blit(event_text, (24, 235))
        surface.blit(event_desc_text, (24, 260))
        surface.blit(quest_text_surface, (24, 285))

        weapon_hint = self.small_font.render("1-3 cambian arma | Espacio: disparar | E: tienda", True, settings.TEXT_COLOR)
        unlocked_text = self.small_font.render(f"Desbloqueadas: {', '.join(unlocked_weapons)}", True, settings.TEXT_COLOR)
        tip = self.small_font.render("Hay efectos visuales para disparos, impactos y recompensas.", True, settings.TEXT_COLOR)
        surface.blit(weapon_hint, (24, settings.SCREEN_HEIGHT - 60))
        surface.blit(unlocked_text, (24, settings.SCREEN_HEIGHT - 38))
        surface.blit(tip, (24, settings.SCREEN_HEIGHT - 16))

    def draw_level_up_menu(self, surface: pygame.Surface, options: list[dict[str, str]], pending_levels: int) -> None:
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        title = self.font.render(f"Subiste de nivel x{pending_levels}", True, settings.TEXT_COLOR)
        prompt = self.small_font.render("Elige una mejora con 1, 2 o 3", True, settings.TEXT_COLOR)
        surface.blit(title, ((settings.SCREEN_WIDTH - title.get_width()) // 2, 120))
        surface.blit(prompt, ((settings.SCREEN_WIDTH - prompt.get_width()) // 2, 160))

        box_width = 250
        box_height = 150
        gap = 22
        start_x = (settings.SCREEN_WIDTH - (box_width * 3 + gap * 2)) // 2
        y = 220

        for index, option in enumerate(options[:3]):
            x = start_x + index * (box_width + gap)
            box = pygame.Rect(x, y, box_width, box_height)
            pygame.draw.rect(surface, (35, 43, 56), box, border_radius=12)
            pygame.draw.rect(surface, (120, 140, 170), box, 2, border_radius=12)

            key_text = self.font.render(str(index + 1), True, settings.TEXT_COLOR)
            title_text = self.small_font.render(option["title"], True, settings.TEXT_COLOR)
            desc_text = self.small_font.render(option["description"], True, settings.TEXT_COLOR)

            surface.blit(key_text, (x + 14, y + 12))
            surface.blit(title_text, (x + 14, y + 52))
            surface.blit(desc_text, (x + 14, y + 88))

    def draw_title_screen(self, surface: pygame.Surface, best_score: int, total_runs: int, best_level: int, difficulty_label: str) -> None:
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.fill((17, 21, 28))
        surface.blit(overlay, (0, 0))

        title = self.font.render("Aventura 2D", True, settings.TEXT_COLOR)
        subtitle = self.small_font.render("Explora, dispara, sube de nivel y vence al mini-jefe", True, settings.TEXT_COLOR)
        start_text = self.small_font.render("Enter o Espacio para empezar", True, settings.TEXT_COLOR)
        controls = self.small_font.render("1: Facil | 2: Normal | 3: Dificil | Enter: empezar", True, settings.TEXT_COLOR)
        save_info = self.small_font.render(
            f"Partidas: {total_runs} | Mejor puntaje: {best_score} | Mejor nivel: {best_level}",
            True,
            settings.TEXT_COLOR,
        )
        difficulty_text = self.small_font.render(f"Dificultad actual: {difficulty_label}", True, settings.TEXT_COLOR)

        surface.blit(title, ((settings.SCREEN_WIDTH - title.get_width()) // 2, 170))
        surface.blit(subtitle, ((settings.SCREEN_WIDTH - subtitle.get_width()) // 2, 225))
        surface.blit(start_text, ((settings.SCREEN_WIDTH - start_text.get_width()) // 2, 305))
        surface.blit(save_info, ((settings.SCREEN_WIDTH - save_info.get_width()) // 2, 350))
        surface.blit(difficulty_text, ((settings.SCREEN_WIDTH - difficulty_text.get_width()) // 2, 380))
        surface.blit(controls, ((settings.SCREEN_WIDTH - controls.get_width()) // 2, 415))

    def draw_pause_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        title = self.font.render("Pausa", True, settings.TEXT_COLOR)
        hint = self.small_font.render("P para continuar | R para reiniciar | Esc para salir", True, settings.TEXT_COLOR)
        surface.blit(title, ((settings.SCREEN_WIDTH - title.get_width()) // 2, 260))
        surface.blit(hint, ((settings.SCREEN_WIDTH - hint.get_width()) // 2, 310))

    def draw_end_screen(
        self,
        surface: pygame.Surface,
        victory: bool,
        score: int,
        play_time: float,
        enemies_defeated: int,
        treasures_collected: int,
        level: int,
    ) -> None:
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        headline = "Victoria" if victory else "Derrota"
        title = self.font.render(headline, True, settings.TEXT_COLOR)
        score_text = self.small_font.render(f"Puntaje final: {score}", True, settings.TEXT_COLOR)
        time_text = self.small_font.render(f"Tiempo jugado: {play_time:.1f} s", True, settings.TEXT_COLOR)
        enemy_text = self.small_font.render(f"Enemigos derrotados: {enemies_defeated}", True, settings.TEXT_COLOR)
        treasure_text = self.small_font.render(f"Tesoros recogidos: {treasures_collected}", True, settings.TEXT_COLOR)
        level_text = self.small_font.render(f"Nivel alcanzado: {level}", True, settings.TEXT_COLOR)
        action_text = self.small_font.render("R para reiniciar | Enter para volver a jugar | Esc para salir", True, settings.TEXT_COLOR)

        start_y = 160
        surface.blit(title, ((settings.SCREEN_WIDTH - title.get_width()) // 2, start_y))
        surface.blit(score_text, ((settings.SCREEN_WIDTH - score_text.get_width()) // 2, start_y + 70))
        surface.blit(time_text, ((settings.SCREEN_WIDTH - time_text.get_width()) // 2, start_y + 105))
        surface.blit(enemy_text, ((settings.SCREEN_WIDTH - enemy_text.get_width()) // 2, start_y + 140))
        surface.blit(treasure_text, ((settings.SCREEN_WIDTH - treasure_text.get_width()) // 2, start_y + 175))
        surface.blit(level_text, ((settings.SCREEN_WIDTH - level_text.get_width()) // 2, start_y + 210))
        surface.blit(action_text, ((settings.SCREEN_WIDTH - action_text.get_width()) // 2, start_y + 280))

    def draw_minimap(
        self,
        surface: pygame.Surface,
        player_rect: pygame.Rect,
        world_size: tuple[int, int],
        zones: list,
        enemies: list,
        shop_zone: pygame.Rect,
    ) -> None:
        minimap_width = 200
        minimap_height = 130
        margin = 20
        map_rect = pygame.Rect(settings.SCREEN_WIDTH - minimap_width - margin, margin, minimap_width, minimap_height)

        pygame.draw.rect(surface, (18, 24, 31), map_rect, border_radius=10)
        pygame.draw.rect(surface, (74, 94, 118), map_rect, 2, border_radius=10)

        scale_x = minimap_width / world_size[0]
        scale_y = minimap_height / world_size[1]

        def scale_rect(rect: pygame.Rect) -> pygame.Rect:
            return pygame.Rect(
                map_rect.x + int(rect.x * scale_x),
                map_rect.y + int(rect.y * scale_y),
                max(2, int(rect.width * scale_x)),
                max(2, int(rect.height * scale_y)),
            )

        for zone in zones:
            zone_color = (74, 108, 132) if not zone.completed else (84, 160, 120)
            pygame.draw.rect(surface, zone_color, scale_rect(zone.rect), 1)

        pygame.draw.rect(surface, (86, 135, 225), scale_rect(shop_zone))

        for enemy in enemies:
            if enemy.alive:
                enemy_dot = scale_rect(enemy.rect)
                pygame.draw.rect(surface, (232, 114, 114), enemy_dot)

        player_dot = scale_rect(player_rect)
        pygame.draw.rect(surface, (92, 242, 156), player_dot)

        label = self.small_font.render("Mapa", True, settings.TEXT_COLOR)
        surface.blit(label, (map_rect.x + 8, map_rect.y + 6))

    def draw_center_message(self, surface: pygame.Surface, message: str) -> None:
        text = self.font.render(message, True, settings.TEXT_COLOR)
        shadow = self.font.render(message, True, (0, 0, 0))
        x = (settings.SCREEN_WIDTH - text.get_width()) // 2
        y = (settings.SCREEN_HEIGHT - text.get_height()) // 2
        surface.blit(shadow, (x + 2, y + 2))
        surface.blit(text, (x, y))
