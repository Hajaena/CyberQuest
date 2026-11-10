"""Écran 1 : menu principal."""
import pygame

from ..settings import COLORS, HEIGHT, WIDTH
from ..sprites import draw_glitch, draw_player
from ..ui import Button, draw_text
from .base import Scene


class MenuScene(Scene):
    ENTRIES = [("Jouer", "name_input"), ("Tableau d'honneur", "leaderboard"), ("Options", "options"), ("Quitter", None)]

    def on_enter(self, **kwargs):
        self.t = 0.0
        self.focus = 0
        self.buttons = [
            Button((WIDTH // 2 - 160, 270 + i * 68, 320, 52), label) for i, (label, _) in enumerate(self.ENTRIES)
        ]
        self._sync_focus()

    def _sync_focus(self):
        for i, b in enumerate(self.buttons):
            b.focused = i == self.focus

    def _activate(self, index):
        self.app.audio.play("click")
        target = self.ENTRIES[index][1]
        if target is None:
            self.app.running = False
        else:
            self.app.change_scene(target)

    def handle_event(self, event):
        for i, b in enumerate(self.buttons):
            if b.handle_event(event):
                self._activate(i)
                return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.focus = (self.focus + 1) % len(self.buttons)
            elif event.key == pygame.K_UP:
                self.focus = (self.focus - 1) % len(self.buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._activate(self.focus)
            self._sync_focus()

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        self.app.background.draw(screen)
        cx = WIDTH // 2
        draw_text(screen, "CYBERQUEST", 104, COLORS["accent"], (cx, 70), "midtop")
        draw_text(screen, "Le Gardien du Réseau", 44, COLORS["text"], (cx, 160), "midtop")
        company = self.app.cfg["company_name"]
        draw_text(screen, f"{company} recrute un(e) Responsable Sécurité...", 26, COLORS["muted"], (cx, 215), "midtop")
        for b in self.buttons:
            b.draw(screen)
        pygame.draw.rect(screen, (74, 86, 128), (0, HEIGHT - 40, WIDTH, 40))
        draw_glitch(screen, 130, HEIGHT - 40, self.t, 1.0)
        draw_player(screen, WIDTH - 130, HEIGHT - 40, self.t)
        draw_text(screen, "Flèches + Entrée ou souris", 20, COLORS["muted"], (cx, HEIGHT - 28), "midtop")
