"""Dessins du jeu (formes simples façon pixel-art) : bâtiment, personnages, mini-événements."""
import math
import random

import pygame

from .settings import COLORS
from .ui import draw_text

FLOOR_TINTS = [(33, 44, 80), (30, 54, 78), (38, 42, 74), (54, 38, 72)]
SLAB = (74, 86, 128)
SKIN = (240, 200, 160)


# ------------------------------------------------------------------ Bâtiment ---
class Building:
    """Coupe d'un immeuble : un niveau du jeu = un étage (niveau 1 en bas)."""

    def __init__(self, rect, names):
        self.rect = pygame.Rect(rect)
        self.names = names
        self.n = len(names)
        self.floor_h = self.rect.height // self.n

    def floor_rect(self, level):
        top = self.rect.bottom - level * self.floor_h
        return pygame.Rect(self.rect.x, top, self.rect.w, self.floor_h)

    def feet_y(self, floor_pos):
        """Ordonnée des pieds du personnage (floor_pos peut être fractionnaire)."""
        return self.rect.bottom - (floor_pos - 1) * self.floor_h - 10

    def draw(self, surface, floor_pos, t, company):
        r = self.rect
        sign = pygame.Rect(r.x + 40, r.y - 30, r.w - 80, 26)
        pygame.draw.rect(surface, (20, 24, 44), sign, border_radius=5)
        pygame.draw.rect(surface, COLORS["panel_border"], sign, 2, border_radius=5)
        draw_text(surface, company.upper(), 22, COLORS["accent"], sign.center, "center")
        pygame.draw.rect(surface, (14, 18, 36), r.inflate(10, 10), border_radius=6)

        current = round(floor_pos)
        for level in range(1, self.n + 1):
            fr = self.floor_rect(level)
            pygame.draw.rect(surface, FLOOR_TINTS[(level - 1) % len(FLOOR_TINTS)], fr.inflate(0, -2))
            pygame.draw.rect(surface, SLAB, (fr.x, fr.bottom - 10, fr.w, 10))
            # fenêtre
            win = pygame.Rect(fr.x + 16, fr.y + 28, 54, 38)
            pygame.draw.rect(surface, (40, 70, 120), win)
            pygame.draw.line(surface, (20, 30, 60), win.midtop, win.midbottom, 2)
            pygame.draw.line(surface, (20, 30, 60), win.midleft, win.midright, 2)
            pygame.draw.rect(surface, (90, 110, 160), win, 2)
            _decor(surface, level, fr, t)
            if level < self.n:
                _stairs(surface, fr)
            draw_text(surface, f"{level}. {self.names[level - 1]}", 18, COLORS["muted"], (fr.x + 8, fr.y + 6))
            if level == current:
                pygame.draw.rect(surface, COLORS["accent"], fr.inflate(0, -2), 2)


def _stairs(surface, fr):
    feet = fr.bottom - 10
    for i in range(5):
        x = fr.right - 58 + i * 9
        h = (i + 1) * 8
        pygame.draw.rect(surface, (62, 74, 118), (x, feet - h, fr.right - 14 - x, h))


def _decor(surface, level, fr, t):
    feet = fr.bottom - 10
    x0 = fr.x
    if level == 1:  # accueil : comptoir + écran
        pygame.draw.rect(surface, (120, 84, 56), (x0 + 140, feet - 26, 84, 26), border_radius=3)
        pygame.draw.rect(surface, (165, 124, 84), (x0 + 140, feet - 30, 84, 6), border_radius=3)
        pygame.draw.rect(surface, (30, 36, 60), (x0 + 168, feet - 52, 28, 20))
        pygame.draw.rect(surface, COLORS["accent"], (x0 + 171, feet - 49, 22, 14))
    elif level == 2:  # open space : deux bureaux avec écrans
        for dx in (132, 188):
            pygame.draw.rect(surface, (110, 90, 70), (x0 + dx, feet - 24, 48, 6))
            pygame.draw.rect(surface, (80, 64, 50), (x0 + dx + 4, feet - 18, 6, 18))
            pygame.draw.rect(surface, (80, 64, 50), (x0 + dx + 38, feet - 18, 6, 18))
            pygame.draw.rect(surface, (25, 30, 50), (x0 + dx + 12, feet - 46, 26, 20))
            pygame.draw.rect(surface, (60, 200, 160), (x0 + dx + 14, feet - 44, 22, 16))
    elif level == 3:  # salle serveur : baies avec LED qui clignotent
        for k, dx in enumerate((128, 162, 196)):
            pygame.draw.rect(surface, (20, 24, 36), (x0 + dx, feet - 70, 28, 70), border_radius=2)
            pygame.draw.rect(surface, (70, 80, 110), (x0 + dx, feet - 70, 28, 70), 2, border_radius=2)
            for i in range(5):
                on = (int(t * 3) + i + k) % 3 != 0
                color = COLORS["accent"] if on else (20, 90, 70)
                if (i + k) % 4 == 0 and on:
                    color = COLORS["danger"]
                pygame.draw.rect(surface, color, (x0 + dx + 6, feet - 62 + i * 12, 6, 6))
                pygame.draw.rect(surface, (50, 58, 84), (x0 + dx + 15, feet - 63 + i * 12, 9, 8))
    else:  # direction : grand bureau, fauteuil, plante, diplôme
        pygame.draw.rect(surface, (96, 62, 44), (x0 + 128, feet - 28, 96, 10), border_radius=2)
        pygame.draw.rect(surface, (70, 44, 32), (x0 + 134, feet - 18, 8, 18))
        pygame.draw.rect(surface, (70, 44, 32), (x0 + 210, feet - 18, 8, 18))
        pygame.draw.rect(surface, (150, 60, 70), (x0 + 196, feet - 50, 14, 24), border_radius=4)
        pygame.draw.rect(surface, (110, 74, 50), (x0 + 100, feet - 14, 14, 14))
        pygame.draw.circle(surface, (40, 150, 80), (x0 + 107, feet - 22), 10)
        pygame.draw.rect(surface, (230, 220, 180), (x0 + 120, fr.y + 30, 34, 24))
        pygame.draw.rect(surface, COLORS["warn"], (x0 + 120, fr.y + 30, 34, 24), 2)


# ---------------------------------------------------------------- Personnages ---
def draw_player(surface, x, feet_y, t, moving=False):
    """Le nouvel employé : chemise bleue, badge blanc."""
    x, y = int(x), int(feet_y)
    swing = math.sin(t * 12) if moving else 0
    bob = int(abs(swing) * 3)
    y -= bob
    pygame.draw.rect(surface, (35, 38, 70), (x - 8, y - 14, 7, 14 + (2 if swing > 0 else 0)))
    pygame.draw.rect(surface, (35, 38, 70), (x + 1, y - 14, 7, 14 + (2 if swing < 0 else 0)))
    pygame.draw.rect(surface, (50, 130, 230), (x - 10, y - 34, 20, 22), border_radius=3)
    pygame.draw.rect(surface, (50, 130, 230), (x - 14, y - 32, 5, 16), border_radius=2)
    pygame.draw.rect(surface, (50, 130, 230), (x + 9, y - 32, 5, 16), border_radius=2)
    pygame.draw.rect(surface, COLORS["white"], (x + 2, y - 28, 6, 8))       # badge
    pygame.draw.rect(surface, COLORS["accent"], (x + 3, y - 27, 4, 2))
    pygame.draw.rect(surface, SKIN, (x - 8, y - 48, 16, 14), border_radius=3)
    pygame.draw.rect(surface, (60, 40, 30), (x - 8, y - 50, 16, 6), border_radius=2)
    pygame.draw.rect(surface, (30, 30, 40), (x - 4, y - 43, 2, 3))
    pygame.draw.rect(surface, (30, 30, 40), (x + 3, y - 43, 2, 3))


def draw_glitch(surface, x, feet_y, t, threat=0.0):
    """Glitch, le hacker à capuche. Les yeux deviennent rouges quand la menace monte."""
    x, y = int(x), int(feet_y)
    rng = random.Random(int(t * 12))
    pygame.draw.rect(surface, (30, 14, 50), (x - 10, y - 14, 8, 14))
    pygame.draw.rect(surface, (30, 14, 50), (x + 2, y - 14, 8, 14))
    pygame.draw.rect(surface, (52, 24, 84), (x - 13, y - 38, 26, 26), border_radius=4)       # sweat
    pygame.draw.rect(surface, (52, 24, 84), (x - 18, y - 36, 6, 18), border_radius=2)
    pygame.draw.rect(surface, (52, 24, 84), (x + 12, y - 36, 6, 18), border_radius=2)
    pygame.draw.rect(surface, (52, 24, 84), (x - 11, y - 56, 22, 20), border_radius=8)       # capuche
    pygame.draw.rect(surface, (8, 6, 14), (x - 7, y - 50, 14, 11), border_radius=3)          # visage
    eye = COLORS["danger"] if threat > 0.7 else (0, 255, 120)
    if int(t * 2) % 5 != 0:
        pygame.draw.rect(surface, eye, (x - 5, y - 46, 3, 3))
        pygame.draw.rect(surface, eye, (x + 2, y - 46, 3, 3))
    pygame.draw.rect(surface, (120, 126, 150), (x + 8, y - 30, 20, 13))                      # laptop
    pygame.draw.rect(surface, (0, 200, 120), (x + 10, y - 28, 16, 8))
    # artefacts « glitch »
    for _ in range(3):
        gx = x + rng.randint(-24, 22)
        gy = y - rng.randint(4, 56)
        color = rng.choice([COLORS["glitch"], (0, 230, 255), COLORS["danger"]])
        pygame.draw.rect(surface, color, (gx, gy, rng.randint(6, 16), 2))


# --------------------------------------------------------- Mini-événements ---
def draw_event(surface, kind, rect, t):
    """Petite illustration associée à une question (e-mail, clé USB, visiteur...)."""
    pygame.draw.rect(surface, (14, 20, 40), rect, border_radius=8)
    pygame.draw.rect(surface, COLORS["panel_border"], rect, 2, border_radius=8)
    cx, cy = rect.center
    blink = int(t * 2) % 2 == 0

    if kind == "email":
        win = rect.inflate(-18, -18)
        pygame.draw.rect(surface, (235, 238, 248), win, border_radius=4)
        pygame.draw.rect(surface, COLORS["danger"], (win.x, win.y, win.w, 18), border_top_left_radius=4, border_top_right_radius=4)
        draw_text(surface, "Nouveau message", 16, COLORS["white"], (win.x + 6, win.y + 3))
        for i in range(3):
            pygame.draw.rect(surface, (170, 176, 196), (win.x + 8, win.y + 28 + i * 12, win.w - 16 - i * 22, 6))
        link = pygame.Rect(win.x + 10, win.bottom - 30, win.w - 20, 22)
        pygame.draw.rect(surface, (60, 90, 220) if blink else (40, 66, 180), link, border_radius=4)
        draw_text(surface, "Cliquez ici !", 18, COLORS["white"], link.center, "center")
    elif kind == "usb":
        body = pygame.Rect(0, 0, 70, 34)
        body.center = (cx + 14, cy)
        pygame.draw.rect(surface, (70, 80, 110), body, border_radius=5)
        pygame.draw.rect(surface, (190, 195, 205), (body.x - 26, body.y + 6, 28, 22))
        pygame.draw.rect(surface, (40, 44, 60), (body.x - 20, body.y + 11, 6, 4))
        pygame.draw.rect(surface, (40, 44, 60), (body.x - 10, body.y + 11, 6, 4))
        if blink:
            draw_text(surface, "?", 32, COLORS["warn"], body.center, "center")
        draw_text(surface, "Clé inconnue", 18, COLORS["muted"], (cx, rect.bottom - 14), "center")
    elif kind == "visiteur":
        pygame.draw.circle(surface, (150, 160, 185), (cx, cy - 22), 15)
        pygame.draw.rect(surface, (90, 100, 130), (cx - 24, cy - 4, 48, 40), border_radius=10)
        pygame.draw.rect(surface, COLORS["danger"], (cx - 12, cy + 6, 24, 16), 2)
        draw_text(surface, "SANS BADGE", 18, COLORS["danger"], (cx, rect.bottom - 14), "center")
    elif kind == "telephone":
        phone = pygame.Rect(0, 0, 40, 72)
        phone.center = (cx, cy - 4)
        pygame.draw.rect(surface, (50, 56, 80), phone, border_radius=8)
        pygame.draw.rect(surface, (0, 140, 110) if blink else (0, 100, 80), phone.inflate(-10, -16), border_radius=4)
        for i in range(1, 3):
            r = pygame.Rect(0, 0, 30 + i * 18, 30 + i * 18)
            r.center = (cx + 4, cy - 12)
            if (int(t * 3) % 3) >= i - 1:
                pygame.draw.arc(surface, COLORS["warn"], r, 0.5, 1.1, 3)
                pygame.draw.arc(surface, COLORS["warn"], r, 2.0, 2.6, 3)
        draw_text(surface, "Appel inconnu", 18, COLORS["muted"], (cx, rect.bottom - 12), "center")
    elif kind == "cadenas":
        pygame.draw.arc(surface, (200, 205, 220), pygame.Rect(cx - 18, cy - 38, 36, 44), 0, math.pi, 6)
        pygame.draw.rect(surface, COLORS["warn"], (cx - 26, cy - 4, 52, 40), border_radius=6)
        pygame.draw.circle(surface, (60, 40, 10), (cx, cy + 12), 6)
        pygame.draw.rect(surface, (60, 40, 10), (cx - 2, cy + 14, 4, 10))
    elif kind == "serveur":
        for i in range(3):
            unit = pygame.Rect(cx - 42, cy - 44 + i * 30, 84, 24)
            pygame.draw.rect(surface, (50, 58, 84), unit, border_radius=3)
            pygame.draw.rect(surface, (20, 24, 36), unit.inflate(-30, -12), border_radius=2)
            on = (int(t * 3) + i) % 2 == 0
            pygame.draw.circle(surface, COLORS["accent"] if on else (20, 90, 70), (unit.right - 10, unit.centery), 4)
            pygame.draw.circle(surface, COLORS["danger"] if not on else (90, 30, 40), (unit.right - 22, unit.centery), 4)
