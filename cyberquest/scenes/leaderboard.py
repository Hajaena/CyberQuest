"""Écran 5 : tableau d'honneur (SQLite)."""
from datetime import datetime

import pygame

from .. import database
from ..settings import COLORS, LEVELS, WIDTH
from ..ui import Button, draw_text
from .base import Scene


def _format_date(raw):
    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
    except ValueError:
        return raw


class LeaderboardScene(Scene):
    def on_enter(self, **kwargs):
        self.rows = database.top_scores(10)
        self.back_btn = Button((WIDTH // 2 - 120, 530, 240, 48), "Retour")

    def handle_event(self, event):
        if self.back_btn.handle_event(event) or (
            event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN)
        ):
            self.app.audio.play("click")
            self.app.change_scene("menu")

    def draw(self, screen):
        self.app.background.draw(screen)
        draw_text(screen, "TABLEAU D'HONNEUR", 60, COLORS["warn"], (WIDTH // 2, 24), "midtop")
        panel = pygame.Rect(80, 96, WIDTH - 160, 416)
        pygame.draw.rect(screen, COLORS["panel"], panel, border_radius=12)
        pygame.draw.rect(screen, COLORS["panel_border"], panel, 2, border_radius=12)

        cols = {"rang": 110, "nom": 175, "score": 470, "niveau": 570, "date": 760}
        for key, label in (("rang", "#"), ("nom", "Nom"), ("score", "Score"), ("niveau", "Étage"), ("date", "Date")):
            draw_text(screen, label, 26, COLORS["muted"], (cols[key], 112))
        pygame.draw.line(screen, COLORS["panel_border"], (100, 140), (panel.right - 20, 140), 1)

        if not self.rows:
            draw_text(screen, "Aucun score pour l'instant. Sois le premier !", 30, COLORS["text"], panel.center, "center")
        for i, (nom, score, niveau, date) in enumerate(self.rows):
            y = 152 + i * 35
            color = COLORS["warn"] if i == 0 else COLORS["text"]
            draw_text(screen, str(i + 1), 28, color, (cols["rang"], y))
            draw_text(screen, nom, 28, color, (cols["nom"], y))
            draw_text(screen, str(score), 28, color, (cols["score"], y))
            lvl = LEVELS[min(niveau, len(LEVELS)) - 1]["nom"]
            draw_text(screen, lvl, 26, color, (cols["niveau"], y + 1))
            draw_text(screen, _format_date(date), 26, COLORS["muted"], (cols["date"], y + 1))
        self.back_btn.draw(screen)
