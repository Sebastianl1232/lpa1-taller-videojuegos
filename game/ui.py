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
    ) -> None:
        hp_text = self.font.render(f"HP: {hp}/{max_hp}", True, settings.TEXT_COLOR)
        level_text = self.font.render(f"Nivel: {level}  XP: {xp}", True, settings.TEXT_COLOR)
        gold_text = self.font.render(f"Oro: {gold}", True, settings.TEXT_COLOR)
        score_text = self.font.render(f"Puntaje: {score}/{settings.OBJECTIVE_SCORE}", True, settings.TEXT_COLOR)
        weapon_text = self.font.render(f"Arma: {active_weapon}", True, settings.TEXT_COLOR)

        surface.blit(hp_text, (24, 20))
        surface.blit(level_text, (24, 50))
        surface.blit(gold_text, (24, 80))
        surface.blit(score_text, (24, 110))
        surface.blit(weapon_text, (24, 140))

        weapon_hint = self.small_font.render("1-3 cambian arma | Espacio: disparar | E: tienda", True, settings.TEXT_COLOR)
        unlocked_text = self.small_font.render(f"Desbloqueadas: {', '.join(unlocked_weapons)}", True, settings.TEXT_COLOR)
        tip = self.small_font.render("Cuando subes de nivel eliges una mejora con 1, 2 o 3.", True, settings.TEXT_COLOR)
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

    def draw_center_message(self, surface: pygame.Surface, message: str) -> None:
        text = self.font.render(message, True, settings.TEXT_COLOR)
        shadow = self.font.render(message, True, (0, 0, 0))
        x = (settings.SCREEN_WIDTH - text.get_width()) // 2
        y = (settings.SCREEN_HEIGHT - text.get_height()) // 2
        surface.blit(shadow, (x + 2, y + 2))
        surface.blit(text, (x, y))
