"""Écran 2 : saisie du nom du joueur."""
import pygame

from ..settings import COLORS, WIDTH
from ..ui import Button, TextInput, draw_text
from .base import Scene


class NameInputScene(Scene):
    def on_enter(self, **kwargs):
        self.t = 0.0
        self.error = ""
        self.input = TextInput((WIDTH // 2 - 240, 260, 480, 64), max_len=16, text=self.app.player_name)
        self.start_btn = Button((WIDTH // 2 - 240, 370, 230, 52), "Commencer")
        self.back_btn = Button((WIDTH // 2 + 10, 370, 230, 52), "Retour")

    def _validate(self):
        name = self.input.text.strip()
        if not name:
            self.error = "Entre ton nom pour continuer."
            return
        self.app.player_name = name
        self.app.audio.play("click")
        self.app.change_scene("game")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_scene("menu")
            return
        if self.input.handle_event(event) or self.start_btn.handle_event(event):
            self._validate()
        elif self.back_btn.handle_event(event):
            self.app.audio.play("click")
            self.app.change_scene("menu")

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        self.app.background.draw(screen)
        cx = WIDTH // 2
        draw_text(screen, "Bienvenue, recrue !", 64, COLORS["accent"], (cx, 90), "midtop")
        draw_text(screen, f"Comment t'appelles-tu ? ({self.app.cfg['company_name']})", 30, COLORS["text"], (cx, 190), "midtop")
        self.input.draw(screen, self.t)
        if self.error:
            draw_text(screen, self.error, 26, COLORS["danger"], (cx, 335), "midtop")
        self.start_btn.draw(screen)
        self.back_btn.draw(screen)
        draw_text(screen, "Entrée pour valider · Échap pour revenir", 22, COLORS["muted"], (cx, 470), "midtop")
