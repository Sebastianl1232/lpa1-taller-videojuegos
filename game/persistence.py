"""Persistencia simple de progreso y estadisticas."""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
import json
from pathlib import Path
from typing import Any


SAVE_FILE = Path(__file__).resolve().parents[1] / "savegame.json"


@dataclass
class GameSave:
    best_score: int = 0
    best_level: int = 1
    total_runs: int = 0
    total_enemies_defeated: int = 0
    total_treasures_collected: int = 0
    total_damage_taken: int = 0
    unlocked_weapons: list[str] = field(default_factory=lambda: ["basic"])
    active_weapon: str = "basic"


def load_game_save() -> GameSave:
    if not SAVE_FILE.exists():
        return GameSave()

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except (OSError, json.JSONDecodeError):
        return GameSave()

    return GameSave(
        best_score=int(data.get("best_score", 0)),
        best_level=int(data.get("best_level", 1)),
        total_runs=int(data.get("total_runs", 0)),
        total_enemies_defeated=int(data.get("total_enemies_defeated", 0)),
        total_treasures_collected=int(data.get("total_treasures_collected", 0)),
        total_damage_taken=int(data.get("total_damage_taken", 0)),
        unlocked_weapons=list(data.get("unlocked_weapons", ["basic"])),
        active_weapon=str(data.get("active_weapon", "basic")),
    )


def save_game_save(game_save: GameSave) -> None:
    payload: dict[str, Any] = asdict(game_save)
    try:
        with SAVE_FILE.open("w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, indent=2, ensure_ascii=False)
    except OSError:
        pass
