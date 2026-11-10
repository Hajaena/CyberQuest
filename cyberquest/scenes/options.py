"""Options : musique, effets, volume, durée du chronomètre (sauvegardées dans config.json)."""
import pygame

from ..settings import COLORS, WIDTH, save_config
from ..ui import Button, draw_text
from .base import Scene


class OptionsScene(Scene):
    def on_enter(self, **kwargs):
        x = 620
        self.music_btn = Button((x, 130, 130, 46), "")
        self.sfx_btn = Button((x, 200, 130, 46), "")
        self.vol_minus = Button((x, 270, 46, 46), "-")
        self.vol_plus = Button((x + 204, 270, 46, 46), "+")
        self.time_minus = Button((x, 340, 46, 46), "-")
        self.time_plus = Button((x + 204, 340, 46, 46), "+")
        self.back_btn = Button((WIDTH // 2 - 120, 500, 240, 50), "Retour")

    def _save(self):
        save_config(self.app.cfg)
        self.app.audio.refresh()
        self.app.audio.play("click")

    def handle_event(self, event):
        cfg = self.app.cfg
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_scene("menu")
        elif self.back_btn.handle_event(event):
            self.app.audio.play("click")
            self.app.change_scene("menu")
        elif self.music_btn.handle_event(event):
            cfg["music_enabled"] = not cfg["music_enabled"]
            self._save()
        elif self.sfx_btn.handle_event(event):
            cfg["sfx_enabled"] = not cfg["sfx_enabled"]
            self._save()
        elif self.vol_minus.handle_event(event):
            cfg["volume"] = round(max(0.0, cfg["volume"] - 0.1), 1)
            self._save()
        elif self.vol_plus.handle_event(event):
            cfg["volume"] = round(min(1.0, cfg["volume"] + 0.1), 1)
            self._save()
        elif self.time_minus.handle_event(event):
            cfg["question_time_seconds"] = max(0, cfg["question_time_seconds"] - 5)
            self._save()
        elif self.time_plus.handle_event(event):
            cfg["question_time_seconds"] = min(60, cfg["question_time_seconds"] + 5)
            self._save()

    def draw(self, screen):
        cfg = self.app.cfg
        self.app.background.draw(screen)
        draw_text(screen, "OPTIONS", 64, COLORS["accent"], (WIDTH // 2, 36), "midtop")
        panel = pygame.Rect(120, 105, WIDTH - 240, 370)
        pygame.draw.rect(screen, COLORS["panel"], panel, border_radius=12)
        pygame.draw.rect(screen, COLORS["panel_border"], panel, 2, border_radius=12)

        labels = ["Musique", "Effets sonores", "Volume", "Temps par question"]
        for i, label in enumerate(labels):
            draw_text(screen, label, 32, COLORS["text"], (160, 140 + i * 70))

        self.music_btn.text = "ON" if cfg["music_enabled"] else "OFF"
        self.sfx_btn.text = "ON" if cfg["sfx_enabled"] else "OFF"
        for b in (self.music_btn, self.sfx_btn, self.vol_minus, self.vol_plus,
                  self.time_minus, self.time_plus, self.back_btn):
            b.draw(screen)

        draw_text(screen, f"{int(cfg['volume'] * 100)} %", 30, COLORS["text"], (620 + 125, 293), "center")
        secs = cfg["question_time_seconds"]
        draw_text(screen, f"{secs} s" if secs else "Sans", 30, COLORS["text"], (620 + 125, 363), "center")
        draw_text(screen, "Les réglages sont enregistrés dans config.json", 22, COLORS["muted"], (WIDTH // 2, 440), "midtop")
