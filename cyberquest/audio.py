"""Gestion des sons 8-bit et de la musique chiptune (tolère l'absence de carte son)."""
import pygame

from . import soundgen
from .settings import SOUNDS_DIR

SOUND_NAMES = ("click", "success", "error", "levelup", "gameover")


class AudioManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.available = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            soundgen.ensure_sounds(SOUNDS_DIR)
            for name in SOUND_NAMES:
                self.sounds[name] = pygame.mixer.Sound(str(SOUNDS_DIR / f"{name}.wav"))
            self.available = True
        except (pygame.error, OSError) as exc:
            print(f"Audio désactivé : {exc}")
        self.apply_volume()

    def apply_volume(self):
        if not self.available:
            return
        volume = float(self.cfg["volume"])
        for sound in self.sounds.values():
            sound.set_volume(volume)
        pygame.mixer.music.set_volume(volume * 0.6)

    def play(self, name):
        if self.available and self.cfg["sfx_enabled"]:
            self.sounds[name].play()

    def start_music(self):
        if self.available and self.cfg["music_enabled"] and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(str(SOUNDS_DIR / "music.wav"))
            pygame.mixer.music.play(-1)

    def stop_music(self):
        if self.available:
            pygame.mixer.music.stop()

    def refresh(self):
        """À appeler après un changement d'options."""
        self.apply_volume()
        if self.cfg["music_enabled"]:
            self.start_music()
        else:
            self.stop_music()
