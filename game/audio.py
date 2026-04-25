"""Efectos de sonido generados por codigo."""

from __future__ import annotations

from array import array
import math

import pygame


class AudioManager:
    def __init__(self) -> None:
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            self.sounds = {
                "shoot": self._create_tone(660, 0.08, 0.22),
                "hit": self._create_tone(240, 0.09, 0.26),
                "pickup": self._create_tone(880, 0.08, 0.2),
                "damage": self._create_tone(140, 0.12, 0.32),
                "levelup": self._create_chord([523, 659, 784], 0.18, 0.2),
                "victory": self._create_chord([392, 523, 659, 784], 0.28, 0.22),
            }
        except pygame.error:
            self.enabled = False
            self.sounds = {}

    def play(self, sound_name: str) -> None:
        if not self.enabled:
            return

        sound = self.sounds.get(sound_name)
        if sound is not None:
            sound.play()

    def _create_tone(self, frequency: float, duration: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        sample_count = max(1, int(sample_rate * duration))
        samples = array("h")

        for index in range(sample_count):
            amplitude = int(32767 * volume * math.sin(2 * math.pi * frequency * (index / sample_rate)))
            samples.append(amplitude)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _create_chord(self, frequencies: list[float], duration: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        sample_count = max(1, int(sample_rate * duration))
        samples = array("h")

        for index in range(sample_count):
            mixed = 0.0
            for frequency in frequencies:
                mixed += math.sin(2 * math.pi * frequency * (index / sample_rate))
            mixed /= len(frequencies)
            amplitude = int(32767 * volume * mixed)
            samples.append(amplitude)

        return pygame.mixer.Sound(buffer=samples.tobytes())
