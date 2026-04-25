"""Render de HUD y textos de estado."""

from __future__ import annotations

import pygame

from game import settings


class UI:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.small_font = pygame.font.SysFont("consolas", 20)

    def draw_hud(self, surface: pygame.Surface, hp: int, max_hp: int, level: int, xp: int, gold: int, score: int) -> None:
        hp_text = self.font.render(f"HP: {hp}/{max_hp}", True, settings.TEXT_COLOR)
        level_text = self.font.render(f"Nivel: {level}  XP: {xp}", True, settings.TEXT_COLOR)
        gold_text = self.font.render(f"Oro: {gold}", True, settings.TEXT_COLOR)
        score_text = self.font.render(f"Puntaje: {score}/{settings.OBJECTIVE_SCORE}", True, settings.TEXT_COLOR)

        surface.blit(hp_text, (24, 20))
        surface.blit(level_text, (24, 50))
        surface.blit(gold_text, (24, 80))
        surface.blit(score_text, (24, 110))

        tip = self.small_font.render("Espacio: disparar | E: tienda (cura 20 HP por 15 oro)", True, settings.TEXT_COLOR)
        surface.blit(tip, (24, settings.SCREEN_HEIGHT - 38))

    def draw_center_message(self, surface: pygame.Surface, message: str) -> None:
        text = self.font.render(message, True, settings.TEXT_COLOR)
        shadow = self.font.render(message, True, (0, 0, 0))
        x = (settings.SCREEN_WIDTH - text.get_width()) // 2
        y = (settings.SCREEN_HEIGHT - text.get_height()) // 2
        surface.blit(shadow, (x + 2, y + 2))
        surface.blit(text, (x, y))
