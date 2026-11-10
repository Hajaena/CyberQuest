"""Écran 4 : résultats, classement et génération de l'attestation PDF."""
import webbrowser

import pygame

from .. import database
from ..certificate import generate_certificate
from ..settings import COLORS, LEVELS, WIDTH
from ..ui import Button, draw_text, draw_wrapped
from .base import Scene


class ResultsScene(Scene):
    def on_enter(self, result=None, **kwargs):
        self.result = result
        self.t = 0.0
        self.message = ""
        self.message_color = COLORS["accent"]
        database.add_score(result["name"], result["score"], result["level"])
        self.rank = database.rank_of(result["score"])

        x1, x2, w = WIDTH // 2 - 290, WIDTH // 2 + 10, 280
        self.cert_btn = Button((x1, 440, w, 48), "Générer mon attestation")
        self.replay_btn = Button((x2, 440, w, 48), "Rejouer")
        self.board_btn = Button((x1, 500, w, 48), "Tableau d'honneur")
        self.menu_btn = Button((x2, 500, w, 48), "Menu principal")

    def _make_certificate(self):
        r = self.result
        try:
            path = generate_certificate(
                r["name"], r["score"], r["level"], r["correct"], r["answered"],
                r["victory"], self.app.cfg["company_name"],
            )
        except ImportError:
            self.message = "reportlab n'est pas installé : pip install -r requirements.txt"
            self.message_color = COLORS["danger"]
            return
        except OSError as exc:
            self.message = f"Impossible d'écrire le PDF : {exc}"
            self.message_color = COLORS["danger"]
            return
        self.message = f"Attestation créée : attestations/{path.name}"
        self.message_color = COLORS["accent"]
        try:
            webbrowser.open(path.as_uri())
        except Exception:  # l'ouverture automatique est facultative
            pass

    def handle_event(self, event):
        if self.cert_btn.handle_event(event):
            self.app.audio.play("click")
            self._make_certificate()
        elif self.replay_btn.handle_event(event):
            self.app.audio.play("click")
            self.app.change_scene("game")
        elif self.board_btn.handle_event(event):
            self.app.audio.play("click")
            self.app.change_scene("leaderboard")
        elif self.menu_btn.handle_event(event) or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            self.app.audio.play("click")
            self.app.change_scene("menu")

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        r = self.result
        cx = WIDTH // 2
        company = self.app.cfg["company_name"]
        self.app.background.draw(screen)
        if r["victory"]:
            draw_text(screen, "MISSION ACCOMPLIE !", 72, COLORS["accent"], (cx, 24), "midtop")
            sub = f"{r['name']}, tu deviens Responsable Sécurité de {company} !"
        else:
            draw_text(screen, "GAME OVER", 72, COLORS["danger"], (cx, 24), "midtop")
            sub = f"Glitch a piraté {company}... mais tu peux retenter ta chance."
        draw_text(screen, sub, 30, COLORS["text"], (cx, 98), "midtop")

        panel = pygame.Rect(cx - 330, 140, 660, 240)
        pygame.draw.rect(screen, COLORS["panel"], panel, border_radius=12)
        pygame.draw.rect(screen, COLORS["panel_border"], panel, 2, border_radius=12)
        draw_text(screen, f"{r['score']} points", 72, COLORS["warn"], (cx, 158), "midtop")

        rate = round(100 * r["correct"] / r["answered"]) if r["answered"] else 0
        level = LEVELS[r["level"] - 1]
        lines = [
            f"Niveau atteint : {r['level']}/{len(LEVELS)} · {level['nom']}",
            f"Bonnes réponses : {r['correct']}/{r['answered']} ({rate} %)",
            f"Meilleure série : x{r['max_combo']}      Classement : #{self.rank}",
        ]
        for i, line in enumerate(lines):
            draw_text(screen, line, 32, COLORS["text"], (cx, 245 + i * 38), "midtop")

        if self.message:
            draw_wrapped(screen, self.message, 22, self.message_color, pygame.Rect(cx - 400, 394, 800, 40), align="center")
        for b in (self.cert_btn, self.replay_btn, self.board_btn, self.menu_btn):
            b.draw(screen)
