"""Écran 3 : le jeu (immeuble, personnage, Glitch, questions, jauge, score)."""
import math
import random

import pygame

from ..questions import pick_for_level
from ..settings import (BASE_POINTS, COLORS, COMBO_STEP, HEIGHT, LEVEL_BONUS, LEVELS,
                        MAX_COMBO_BONUS, MAX_TIME_BONUS, WIDTH)
from ..sprites import Building, draw_event, draw_glitch, draw_player
from ..ui import Button, draw_bar, draw_text, draw_wrapped
from .base import Scene

PANEL = pygame.Rect(330, 76, 610, 504)
BUILDING_RECT = pygame.Rect(20, 100, 290, 480)
FEEDBACK_BOX = pygame.Rect(PANEL.x + 10, 292, PANEL.w - 20, PANEL.bottom - 292 - 10)
ANSWER_KEYS = (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4)
CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)


class GameScene(Scene):
    # États : intro -> question -> feedback -> (question | climb) ... gameover
    def on_enter(self, **kwargs):
        cfg = self.app.cfg
        self.max_security = max(1, cfg["security_max"])
        self.penalty = cfg["security_penalty"]
        self.heal = cfg["security_heal"]
        self.time_limit = cfg["question_time_seconds"]
        self.per_level = cfg["questions_per_level"]

        self.building = Building(BUILDING_RECT, [lv["nom"] for lv in LEVELS])
        self.t = 0.0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.correct = 0
        self.answered = 0
        self.security = self.max_security
        self.shown_security = float(self.max_security)
        self.flash = 0.0
        self.flash_color = COLORS["danger"]
        self.feedback = None
        self.current = None
        self.answer_buttons = []
        self.time_left = 0.0
        self.floor_pos = 1.0
        self.climb_victory = False
        self.continue_btn = Button((FEEDBACK_BOX.right - 190, FEEDBACK_BOX.bottom - 52, 170, 40), "Continuer")
        self.q_list = []
        self.q_index = 0
        self.level = 1
        self.px = BUILDING_RECT.left + 95
        self.start_level(1)

    # ----------------------------------------------------------- logique ---
    def start_level(self, level):
        self.level = level
        self.floor_target = level
        self.q_list = pick_for_level(self.app.questions, level, self.per_level)
        self.q_index = 0
        if not self.q_list:  # aucun contenu pour cet étage : on passe au suivant
            if level >= len(LEVELS):
                self.finish(True)
            else:
                self.start_level(level + 1)
            return
        self.state = "intro"
        self.timer = 3.0

    def target_px(self):
        n = max(1, len(self.q_list))
        left = self.building.rect.left + 95
        right = self.building.rect.right - 50
        return left + (right - left) * (self.q_index / n)

    def begin_question(self):
        self.current = self.q_list[self.q_index]
        self.time_left = float(self.time_limit)
        self.answer_buttons = []
        for i, text in enumerate(self.current["choix"]):
            rect = pygame.Rect(PANEL.x + 20, PANEL.y + 224 + i * 64, PANEL.w - 40, 56)
            self.answer_buttons.append(Button(rect, f"{i + 1}.  {text}", size=25, align="left"))
        self.state = "question"

    def answer(self, idx):
        """idx = index du choix, ou None si le temps est écoulé."""
        q = self.current
        correct = idx == q["bonne_reponse"]
        self.answered += 1
        fb = {"idx": idx, "correct": correct, "timeout": idx is None, "points": 0, "detail": ""}
        if correct:
            self.correct += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            time_bonus = int(MAX_TIME_BONUS * self.time_left / self.time_limit) if self.time_limit > 0 else 0
            combo_bonus = min(MAX_COMBO_BONUS, COMBO_STEP * (self.combo - 1))
            fb["points"] = BASE_POINTS + time_bonus + combo_bonus
            fb["detail"] = f"base {BASE_POINTS} + rapidité {time_bonus} + série {combo_bonus}"
            self.score += fb["points"]
            self.security = min(self.max_security, self.security + self.heal)
            self.flash_color = COLORS["accent"]
            self.app.audio.play("success")
        else:
            self.combo = 0
            self.security = max(0, self.security - self.penalty)
            fb["detail"] = f"-{self.penalty} sécurité : Glitch avance !"
            self.flash_color = COLORS["danger"]
            self.app.audio.play("error")
        self.flash = 0.35
        self.feedback = fb
        self.state = "feedback"

    def next_step(self):
        if self.security <= 0:
            self.state = "gameover"
            self.timer = 2.6
            self.app.audio.play("gameover")
            return
        self.q_index += 1
        if self.q_index >= len(self.q_list):
            self.end_level()
        else:
            self.begin_question()

    def end_level(self):
        self.score += LEVEL_BONUS
        self.app.audio.play("levelup")
        self.climb_victory = self.level >= len(LEVELS)
        if not self.climb_victory:
            self.floor_target = self.level + 1  # le personnage monte d'un étage
        self.state = "climb"
        self.timer = 3.0

    def finish(self, victory):
        self.app.change_scene("results", result={
            "name": self.app.player_name, "score": self.score, "level": self.level,
            "correct": self.correct, "answered": self.answered,
            "max_combo": self.max_combo, "victory": victory,
        })

    # ------------------------------------------------------------ boucle ---
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_scene("menu")
            return
        clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        confirm = event.type == pygame.KEYDOWN and event.key in CONFIRM_KEYS

        if self.state == "intro" and (clicked or confirm):
            self.begin_question()
        elif self.state == "question":
            for i, button in enumerate(self.answer_buttons):
                if button.handle_event(event):
                    self.answer(i)
                    return
            if event.type == pygame.KEYDOWN and event.key in ANSWER_KEYS:
                idx = ANSWER_KEYS.index(event.key)
                if idx < len(self.answer_buttons):
                    self.answer(idx)
        elif self.state == "feedback":
            if self.continue_btn.handle_event(event) or confirm:
                self.app.audio.play("click")
                self.next_step()
        elif self.state == "climb" and (clicked or confirm):
            self.timer = 0

    def update(self, dt):
        self.t += dt
        self.px += (self.target_px() - self.px) * min(1.0, dt * 3.5)
        self.shown_security += (self.security - self.shown_security) * min(1.0, dt * 4)
        self.flash = max(0.0, self.flash - dt)
        if self.floor_pos < self.floor_target:
            self.floor_pos = min(float(self.floor_target), self.floor_pos + dt * 1.2)

        if self.state == "intro":
            self.timer -= dt
            if self.timer <= 0:
                self.begin_question()
        elif self.state == "question" and self.time_limit > 0:
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.answer(None)
        elif self.state == "climb":
            self.timer -= dt
            if self.timer <= 0:
                if self.climb_victory:
                    self.finish(True)
                else:
                    self.start_level(self.level + 1)
        elif self.state == "gameover":
            self.timer -= dt
            if self.timer <= 0:
                self.finish(False)

    # ------------------------------------------------------------ dessin ---
    def draw(self, screen):
        self.app.background.draw(screen)
        self._draw_world(screen)
        self._draw_panel(screen)
        self._draw_hud(screen)
        if self.flash > 0:
            veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            veil.fill((*self.flash_color, int(110 * self.flash / 0.35)))
            screen.blit(veil, (0, 0))
        if self.state == "gameover":
            self._draw_glitch_effect(screen)

    def _draw_hud(self, screen):
        pygame.draw.rect(screen, COLORS["panel"], (0, 0, WIDTH, 64))
        pygame.draw.line(screen, COLORS["panel_border"], (0, 64), (WIDTH, 64), 2)
        draw_text(screen, self.app.player_name, 22, COLORS["muted"], (20, 8))
        draw_text(screen, f"Score {self.score}", 34, COLORS["warn"], (20, 28))
        combo_color = COLORS["accent"] if self.combo >= 2 else COLORS["muted"]
        draw_text(screen, f"Série x{self.combo}", 30, combo_color, (230, 22))
        draw_text(screen, "Sécurité", 22, COLORS["muted"], (390, 6))
        ratio = self.shown_security / self.max_security
        color = COLORS["accent"] if ratio > 0.5 else COLORS["warn"] if ratio > 0.25 else COLORS["danger"]
        draw_bar(screen, pygame.Rect(390, 28, 220, 22), ratio, color)
        draw_text(screen, f"{int(round(self.security / self.max_security * 100))} %", 20, COLORS["white"], (500, 39), "center")
        draw_text(screen, f"Niveau {self.level}/{len(LEVELS)}", 28, COLORS["text"], (WIDTH - 20, 10), "topright")
        draw_text(screen, LEVELS[self.level - 1]["nom"], 22, COLORS["muted"], (WIDTH - 20, 38), "topright")

    def _draw_world(self, screen):
        b = self.building
        b.draw(screen, self.floor_pos, self.t, self.app.cfg["company_name"])
        feet = b.feet_y(self.floor_pos)
        moving = abs(self.px - self.target_px()) > 3 or abs(self.floor_pos - self.floor_target) > 0.01
        threat = 1.0 - self.shown_security / self.max_security
        left = b.rect.left + 28
        gx = left + max(0.0, self.px - 48 - left) * threat
        draw_glitch(screen, gx, feet, self.t, threat)
        draw_player(screen, self.px, feet, self.t, moving)

    def _panel_frame(self, screen):
        pygame.draw.rect(screen, COLORS["panel"], PANEL, border_radius=12)
        pygame.draw.rect(screen, COLORS["panel_border"], PANEL, 2, border_radius=12)

    def _draw_panel(self, screen):
        self._panel_frame(screen)
        if self.state == "intro":
            self._draw_intro(screen)
        elif self.state in ("question", "feedback"):
            self._draw_question(screen)
            if self.state == "feedback":
                self._draw_feedback(screen)
        elif self.state == "climb":
            self._draw_climb(screen)
        elif self.state == "gameover":
            self._draw_gameover(screen)

    def _draw_intro(self, screen):
        cx = PANEL.centerx
        lv = LEVELS[self.level - 1]
        draw_text(screen, f"NIVEAU {self.level}", 70, COLORS["accent"], (cx, PANEL.y + 50), "midtop")
        draw_text(screen, lv["nom"], 48, COLORS["text"], (cx, PANEL.y + 130), "midtop")
        draw_text(screen, lv["theme"], 30, COLORS["warn"], (cx, PANEL.y + 182), "midtop")
        intro = lv["intro"].format(company=self.app.cfg["company_name"])
        draw_wrapped(screen, intro, 28, COLORS["muted"], pygame.Rect(PANEL.x + 50, PANEL.y + 250, PANEL.w - 100, 120), spacing=6, align="center")
        if int(self.t * 2) % 2 == 0:
            draw_text(screen, "Clique ou appuie sur Entrée pour commencer", 24, COLORS["text"], (cx, PANEL.bottom - 50), "midtop")

    def _draw_question(self, screen):
        q = self.current
        theme = q.get("theme", LEVELS[self.level - 1]["theme"])
        draw_text(screen, f"Question {self.q_index + 1}/{len(self.q_list)}  ·  {theme}", 22, COLORS["muted"], (PANEL.x + 20, PANEL.y + 14))
        if self.time_limit > 0:
            ratio = self.time_left / self.time_limit
            color = COLORS["accent"] if ratio > 0.5 else COLORS["warn"] if ratio > 0.25 else COLORS["danger"]
            draw_bar(screen, pygame.Rect(PANEL.x + 20, PANEL.y + 40, PANEL.w - 40, 10), ratio, color)
            draw_text(screen, f"{math.ceil(self.time_left)} s", 24, color, (PANEL.right - 20, PANEL.y + 12), "topright")

        text_w = PANEL.w - 40
        event = q.get("evenement")
        if event:
            card = pygame.Rect(PANEL.right - 20 - 170, PANEL.y + 62, 170, 130)
            draw_event(screen, event, card, self.t)
            text_w -= 170 + 16
        draw_wrapped(screen, q["question"], 28, COLORS["text"], pygame.Rect(PANEL.x + 20, PANEL.y + 64, text_w, 150), spacing=4)

        if self.state == "question":
            for b in self.answer_buttons:
                b.draw(screen)

    def _draw_feedback(self, screen):
        fb, q = self.feedback, self.current
        color = COLORS["accent"] if fb["correct"] else COLORS["danger"]
        pygame.draw.rect(screen, (14, 20, 40), FEEDBACK_BOX, border_radius=10)
        pygame.draw.rect(screen, color, FEEDBACK_BOX, 3, border_radius=10)
        x, y, w = FEEDBACK_BOX.x + 18, FEEDBACK_BOX.y + 12, FEEDBACK_BOX.w - 36

        if fb["correct"]:
            verdict = "Bonne réponse !"
        elif fb["timeout"]:
            verdict = "Temps écoulé !"
        else:
            verdict = "Mauvaise réponse..."
        draw_text(screen, verdict, 38, color, (x, y))
        draw_text(screen, f"+{fb['points']} pts" if fb["correct"] else "", 34, COLORS["warn"], (FEEDBACK_BOX.right - 18, y + 2), "topright")
        y += 44
        draw_text(screen, fb["detail"], 22, COLORS["muted"], (x, y))
        y += 28
        if not fb["correct"]:
            good = q["choix"][q["bonne_reponse"]]
            y = draw_wrapped(screen, f"Bonne réponse : {good}", 24, COLORS["accent"], pygame.Rect(x, y, w, 60), spacing=2) + 4
        draw_wrapped(screen, q["explication"], 24, COLORS["text"], pygame.Rect(x, y, w, 120), spacing=3)
        self.continue_btn.draw(screen)

    def _draw_climb(self, screen):
        cx = PANEL.centerx
        if self.climb_victory:
            draw_text(screen, "FÉLICITATIONS !", 64, COLORS["accent"], (cx, PANEL.y + 90), "midtop")
            draw_text(screen, "Glitch est repoussé.", 38, COLORS["text"], (cx, PANEL.y + 170), "midtop")
            draw_text(screen, "Tu deviens Responsable Sécurité !", 38, COLORS["warn"], (cx, PANEL.y + 214), "midtop")
        else:
            nxt = LEVELS[self.level]["nom"]
            draw_text(screen, "ÉTAGE SÉCURISÉ !", 60, COLORS["accent"], (cx, PANEL.y + 90), "midtop")
            draw_text(screen, f"Bonus d'étage : +{LEVEL_BONUS} pts", 36, COLORS["warn"], (cx, PANEL.y + 170), "midtop")
            draw_text(screen, f"Direction l'étage suivant : {nxt}", 32, COLORS["text"], (cx, PANEL.y + 220), "midtop")
        draw_text(screen, f"Score : {self.score}", 40, COLORS["text"], (cx, PANEL.y + 300), "midtop")

    def _draw_gameover(self, screen):
        cx = PANEL.centerx
        draw_text(screen, "SYSTÈME COMPROMIS", 58, COLORS["danger"], (cx, PANEL.y + 110), "midtop")
        company = self.app.cfg["company_name"]
        draw_text(screen, f"Glitch a pris le contrôle de {company}...", 32, COLORS["text"], (cx, PANEL.y + 200), "midtop")

    def _draw_glitch_effect(self, screen):
        rng = random.Random(int(self.t * 20))
        for _ in range(14):
            color = rng.choice([COLORS["glitch"], (0, 230, 255), COLORS["danger"], COLORS["accent"]])
            y = rng.randint(0, HEIGHT)
            pygame.draw.rect(screen, color, (rng.randint(0, WIDTH - 200), y, rng.randint(40, 300), rng.randint(2, 8)))
