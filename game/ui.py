"""Render de HUD y textos de estado."""

from __future__ import annotations

import pygame

from game import settings


class UI:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.small_font = pygame.font.SysFont("consolas", 20)
        self.large_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.title_animation_time = 0.0

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

    def _update_title_animation(self, dt: float) -> None:
        """Actualiza el contador de animación del título."""
        self.title_animation_time += dt

    def _get_pulse_value(self, frequency: float = 2.0) -> float:
        """Retorna un valor entre 0 y 1 para efectos de pulseo."""
        import math
        return (math.sin(self.title_animation_time * frequency) + 1) / 2

    def _draw_background_pattern(self, surface: pygame.Surface) -> None:
        """Dibuja un patrón decorativo en el fondo del título."""
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.fill((17, 21, 28))
        
        # Patrón de cuadrícula sutil
        for x in range(0, settings.SCREEN_WIDTH, 60):
            for y in range(0, settings.SCREEN_HEIGHT, 60):
                pygame.draw.line(overlay, (35, 43, 56), (x, 0), (x, settings.SCREEN_HEIGHT), 1)
                pygame.draw.line(overlay, (35, 43, 56), (0, y), (settings.SCREEN_WIDTH, y), 1)
        
        # Decoraciones en las esquinas
        corner_size = 40
        pygame.draw.rect(overlay, (74, 108, 132), (0, 0, corner_size, corner_size), 2)
        pygame.draw.rect(overlay, (74, 108, 132), (settings.SCREEN_WIDTH - corner_size, 0, corner_size, corner_size), 2)
        pygame.draw.rect(overlay, (74, 108, 132), (0, settings.SCREEN_HEIGHT - corner_size, corner_size, corner_size), 2)
        pygame.draw.rect(overlay, (74, 108, 132), (settings.SCREEN_WIDTH - corner_size, settings.SCREEN_HEIGHT - corner_size, corner_size, corner_size), 2)
        
        surface.blit(overlay, (0, 0))

    def draw_title_screen(
        self, 
        surface: pygame.Surface, 
        best_score: int, 
        total_runs: int, 
        best_level: int, 
        difficulty_label: str,
        current_difficulty: str = "normal"
    ) -> None:
        """Dibuja la pantalla de título con UI mejorada."""
        self._draw_background_pattern(surface)
        
        # Título principal con efecto de pulseo
        pulse_intensity = self._get_pulse_value(1.5)
        title_color = (
            int(120 + pulse_intensity * 50),
            int(200 + pulse_intensity * 55),
            int(120 + pulse_intensity * 50)
        )
        title = self.large_font.render("AVENTURA 2D", True, title_color)
        surface.blit(title, ((settings.SCREEN_WIDTH - title.get_width()) // 2, 80))
        
        # Subtítulo
        subtitle = self.font.render("Explora, dispara y vence al mini-jefe", True, (150, 180, 200))
        surface.blit(subtitle, ((settings.SCREEN_WIDTH - subtitle.get_width()) // 2, 160))
        
        # Sección de estadísticas
        stats_y = 240
        save_info = self.small_font.render(
            f"Partidas: {total_runs}  |  Mejor puntaje: {best_score}  |  Mejor nivel: {best_level}",
            True,
            (100, 140, 180)
        )
        surface.blit(save_info, ((settings.SCREEN_WIDTH - save_info.get_width()) // 2, stats_y))
        
        # Línea decorativa
        line_y = 300
        pygame.draw.line(surface, (74, 108, 132), (60, line_y), (settings.SCREEN_WIDTH - 60, line_y), 2)
        
        # Sección de selección de dificultad
        difficulties = [
            ("Fácil", "easy", (100, 180, 80)),
            ("Normal", "normal", (150, 150, 150)),
            ("Difícil", "hard", (220, 100, 100))
        ]
        
        box_width = 140
        box_height = 90
        gap = 20
        start_x = (settings.SCREEN_WIDTH - (box_width * 3 + gap * 2)) // 2
        diff_y = 350
        
        for i, (label, key, base_color) in enumerate(difficulties):
            x = start_x + i * (box_width + gap)
            is_selected = (key == current_difficulty)
            
            # Caja de dificultad
            box_color = base_color if is_selected else (50, 60, 80)
            border_width = 3 if is_selected else 1
            border_color = (255, 200, 100) if is_selected else base_color
            
            pygame.draw.rect(surface, box_color, (x, diff_y, box_width, box_height), border_radius=8)
            pygame.draw.rect(surface, border_color, (x, diff_y, box_width, box_height), border_width, border_radius=8)
            
            # Texto de dificultad
            diff_text = self.font.render(label, True, border_color)
            text_y = diff_y + (box_height - diff_text.get_height()) // 2 - 15
            surface.blit(diff_text, (x + (box_width - diff_text.get_width()) // 2, text_y))
            
            # Número de tecla
            key_text = self.small_font.render(f"[{i + 1}]", True, (150, 150, 150))
            surface.blit(key_text, (x + (box_width - key_text.get_width()) // 2, diff_y + box_height - 28))
            
            # Indicador de selección
            if is_selected:
                pulse = self._get_pulse_value(3.0) * 0.3 + 0.7
                indicator_color = tuple(int(c * pulse) for c in border_color)
                pygame.draw.circle(surface, indicator_color, (x + box_width // 2, diff_y - 15), 6)
        
        # Instrucciones
        instructions_y = 500
        start_hint = self.font.render("ENTER para jugar", True, (100, 200, 150))
        surface.blit(start_hint, ((settings.SCREEN_WIDTH - start_hint.get_width()) // 2, instructions_y))
        
        controls = self.small_font.render("W/A/S/D o Flechas: mover  |  Espacio: disparar  |  E: tienda  |  P: pausa  |  L: logros", True, (120, 140, 160))
        surface.blit(controls, ((settings.SCREEN_WIDTH - controls.get_width()) // 2, instructions_y + 50))

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

    def draw_achievement_notification(
        self, surface: pygame.Surface, achievement_icon: str, achievement_name: str, achievement_desc: str
    ) -> None:
        """Dibuja una notificación de logro desbloqueado en la esquina inferior derecha."""
        box_width = 320
        box_height = 90
        margin = 20
        x = settings.SCREEN_WIDTH - box_width - margin
        y = settings.SCREEN_HEIGHT - box_height - margin

        # Fondo del cuadro
        pygame.draw.rect(surface, (35, 43, 56), (x, y, box_width, box_height), border_radius=10)
        pygame.draw.rect(surface, (100, 200, 150), (x, y, box_width, box_height), 3, border_radius=10)

        # Icono
        icon_font = pygame.font.SysFont("consolas", 40, bold=True)
        icon_text = icon_font.render(achievement_icon, True, (100, 200, 150))
        surface.blit(icon_text, (x + 15, y + 12))

        # Texto "Logro desbloqueado"
        label = self.small_font.render("LOGRO DESBLOQUEADO", True, (100, 200, 150))
        surface.blit(label, (x + 65, y + 10))

        # Nombre del logro
        name_text = self.small_font.render(achievement_name, True, (255, 255, 255))
        surface.blit(name_text, (x + 65, y + 32))

        # Descripción
        desc_font = pygame.font.SysFont("consolas", 16)
        desc_text = desc_font.render(achievement_desc, True, (180, 180, 180))
        surface.blit(desc_text, (x + 65, y + 55))

    def draw_achievements_menu(
        self, surface: pygame.Surface, achievements_data: dict, unlocked_count: int, total_count: int
    ) -> None:
        """Dibuja un menú de logros."""
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        title = self.font.render(f"LOGROS ({unlocked_count}/{total_count})", True, (100, 200, 150))
        surface.blit(title, ((settings.SCREEN_WIDTH - title.get_width()) // 2, 40))

        # Mostrar logros en una cuadrícula
        entries = []
        for ach_id, ach in achievements_data.items():
            icon = ach["icon"]
            name = ach["name"]
            description = ach["description"]
            unlocked = ach["unlocked"]
            entries.append((icon, name, description, unlocked))

        # Renderizar en dos columnas
        cols = 2
        rows = (len(entries) + cols - 1) // cols
        box_width = (settings.SCREEN_WIDTH - 100) // cols
        box_height = 100
        start_y = 120

        for idx, (icon, name, description, unlocked) in enumerate(entries):
            row = idx // cols
            col = idx % cols
            x = 40 + col * box_width
            y = start_y + row * box_height

            # Fondo
            color = (50, 80, 60) if unlocked else (50, 50, 60)
            pygame.draw.rect(surface, color, (x, y, box_width - 20, box_height - 10), border_radius=5)
            pygame.draw.rect(surface, (100, 200, 150) if unlocked else (80, 80, 100), (x, y, box_width - 20, box_height - 10), 2, border_radius=5)

            # Icono
            icon_text = self.font.render(icon, True, (100, 200, 150) if unlocked else (120, 120, 120))
            surface.blit(icon_text, (x + 10, y + 8))

            # Nombre
            name_text = self.small_font.render(name, True, (255, 255, 255) if unlocked else (150, 150, 150))
            surface.blit(name_text, (x + 50, y + 8))

            # Descripción
            desc_font = pygame.font.SysFont("consolas", 14)
            desc_text = desc_font.render(description, True, (180, 180, 180) if unlocked else (100, 100, 100))
            surface.blit(desc_text, (x + 50, y + 35))

            # Indicador de completado
            if unlocked:
                status_text = self.small_font.render("✓", True, (100, 200, 150))
                surface.blit(status_text, (x + box_width - 40, y + 8))

        hint = self.small_font.render("Esc para cerrar", True, settings.TEXT_COLOR)
        surface.blit(hint, ((settings.SCREEN_WIDTH - hint.get_width()) // 2, settings.SCREEN_HEIGHT - 30))
