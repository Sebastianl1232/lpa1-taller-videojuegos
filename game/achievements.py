"""Sistema de logros y badges."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Achievement:
    """Define un logro del juego."""
    id: str
    name: str
    description: str
    icon: str  # Emoji o símbolo
    unlocked: bool = False
    progress: int = 0
    max_progress: int = 1
    
    def is_completed(self) -> bool:
        """Retorna True si el logro está completado."""
        return self.progress >= self.max_progress


class AchievementManager:
    """Gestiona los logros y su progreso."""
    
    def __init__(self) -> None:
        self.achievements: dict[str, Achievement] = {}
        self._initialize_achievements()
        self._newly_unlocked: list[str] = []
    
    def _initialize_achievements(self) -> None:
        """Define todos los logros disponibles."""
        achievements = [
            Achievement(
                id="first_enemy",
                name="Primer disparo",
                description="Derrota tu primer enemigo",
                icon="🎯",
                max_progress=1
            ),
            Achievement(
                id="slayer_10",
                name="Cazador de 10",
                description="Derrota 10 enemigos",
                icon="⚔️",
                max_progress=10
            ),
            Achievement(
                id="slayer_50",
                name="Cazador de 50",
                description="Derrota 50 enemigos",
                icon="🔥",
                max_progress=50
            ),
            Achievement(
                id="treasure_hunter",
                name="Cazador de tesoros",
                description="Recoge 5 tesoros",
                icon="💎",
                max_progress=5
            ),
            Achievement(
                id="treasure_master",
                name="Maestro de tesoros",
                description="Recoge 20 tesoros",
                icon="👑",
                max_progress=20
            ),
            Achievement(
                id="level_5",
                name="En ascenso",
                description="Alcanza nivel 5",
                icon="📈",
                max_progress=5
            ),
            Achievement(
                id="level_10",
                name="Héroe experimentado",
                description="Alcanza nivel 10",
                icon="⭐",
                max_progress=10
            ),
            Achievement(
                id="all_weapons",
                name="Arsenal completo",
                description="Desbloquea las 3 armas",
                icon="🎖️",
                max_progress=3
            ),
            Achievement(
                id="miniboss_defeated",
                name="Vencedor del mini-jefe",
                description="Derrota al mini-jefe",
                icon="🐉",
                max_progress=1
            ),
            Achievement(
                id="hard_mode",
                name="Dificultad extrema",
                description="Completa el juego en difícil",
                icon="💀",
                max_progress=1
            ),
            Achievement(
                id="survivor",
                name="Superviviente",
                description="Sobrevive 5 minutos sin daño",
                icon="🛡️",
                max_progress=1
            ),
            Achievement(
                id="rich",
                name="Adinerado",
                description="Acumula 500 de oro",
                icon="💰",
                max_progress=500
            ),
            Achievement(
                id="speed_run",
                name="Velocidad",
                description="Completa el juego en menos de 3 minutos",
                icon="⚡",
                max_progress=180  # segundos
            ),
            Achievement(
                id="perfect_zone",
                name="Sector perfecto",
                description="Completa una zona sin morir",
                icon="🎖️",
                max_progress=1
            ),
            Achievement(
                id="first_victory",
                name="Primera victoria",
                description="Gana tu primer juego",
                icon="🏆",
                max_progress=1
            ),
        ]
        
        for achievement in achievements:
            self.achievements[achievement.id] = achievement
    
    def update_progress(self, achievement_id: str, progress: int) -> None:
        """Actualiza el progreso de un logro."""
        if achievement_id not in self.achievements:
            return
        
        achievement = self.achievements[achievement_id]
        old_progress = achievement.progress
        
        # Incrementar progreso hasta el máximo
        achievement.progress = min(progress, achievement.max_progress)
        
        # Marcar como desbloqueado si se completa
        if achievement.is_completed() and not achievement.unlocked:
            achievement.unlocked = True
            self._newly_unlocked.append(achievement_id)
    
    def increment_progress(self, achievement_id: str, amount: int = 1) -> None:
        """Incrementa el progreso de un logro."""
        if achievement_id not in self.achievements:
            return
        
        achievement = self.achievements[achievement_id]
        self.update_progress(achievement_id, achievement.progress + amount)
    
    def unlock(self, achievement_id: str) -> None:
        """Desbloquea directamente un logro."""
        if achievement_id not in self.achievements:
            return
        
        achievement = self.achievements[achievement_id]
        if not achievement.unlocked:
            achievement.unlocked = True
            achievement.progress = achievement.max_progress
            self._newly_unlocked.append(achievement_id)
    
    def get_newly_unlocked(self) -> list[str]:
        """Retorna los logros recientemente desbloqueados y los limpia."""
        result = self._newly_unlocked.copy()
        self._newly_unlocked.clear()
        return result
    
    def get_unlocked_count(self) -> int:
        """Retorna la cantidad de logros desbloqueados."""
        return sum(1 for ach in self.achievements.values() if ach.unlocked)
    
    def get_total_count(self) -> int:
        """Retorna el total de logros."""
        return len(self.achievements)
    
    def get_progress_percentage(self) -> int:
        """Retorna el porcentaje de logros completados."""
        if self.get_total_count() == 0:
            return 0
        return int((self.get_unlocked_count() / self.get_total_count()) * 100)
    
    def to_dict(self) -> dict[str, dict]:
        """Convierte los logros a diccionario para guardar."""
        return {
            ach_id: {
                "unlocked": ach.unlocked,
                "progress": ach.progress
            }
            for ach_id, ach in self.achievements.items()
        }
    
    def from_dict(self, data: dict[str, dict]) -> None:
        """Carga los logros desde un diccionario guardado."""
        for ach_id, ach_data in data.items():
            if ach_id in self.achievements:
                self.achievements[ach_id].unlocked = ach_data.get("unlocked", False)
                self.achievements[ach_id].progress = ach_data.get("progress", 0)
