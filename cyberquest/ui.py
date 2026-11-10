"""Composants d'interface réutilisables : texte, boutons, barres, saisie, fond animé."""
import random

import pygame

from .settings import COLORS

_fonts = {}


def get_font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(None, size)
    return _fonts[size]


def draw_text(surface, text, size, color, pos, anchor="topleft"):
    img = get_font(size).render(text, True, color)
    rect = img.get_rect(**{anchor: pos})
    surface.blit(img, rect)
    return rect


def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            test = f"{line} {word}" if line else word
            if font.size(test)[0] <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_wrapped(surface, text, size, color, rect, spacing=4, align="left"):
    """Dessine du texte avec retour à la ligne ; retourne le y suivant."""
    font = get_font(size)
    y = rect.top
    for line in wrap_text(text, font, rect.width):
        img = font.render(line, True, color)
        x = rect.x if align == "left" else rect.centerx - img.get_width() // 2
        surface.blit(img, (x, y))
        y += font.get_linesize() + spacing
    return y


def draw_bar(surface, rect, ratio, color, back=(24, 30, 56)):
    ratio = max(0.0, min(1.0, ratio))
    radius = rect.h // 2
    pygame.draw.rect(surface, back, rect, border_radius=radius)
    if ratio > 0:
        fill = pygame.Rect(rect.x, rect.y, max(rect.h, int(rect.w * ratio)), rect.h)
        pygame.draw.rect(surface, color, fill, border_radius=radius)
    pygame.draw.rect(surface, COLORS["panel_border"], rect, 2, border_radius=radius)


class Button:
    def __init__(self, rect, text, size=28, align="center"):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.size = size
        self.align = align
        self.enabled = True
        self.focused = False
        self.override = None  # couleur imposée (ex. bonne / mauvaise réponse)

    def handle_event(self, event):
        return (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface):
        hovered = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        if self.override:
            color = self.override
        else:
            color = COLORS["button_hover"] if (hovered or self.focused) else COLORS["button"]
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        border = COLORS["accent"] if (hovered or self.focused) else COLORS["panel_border"]
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)

        font = get_font(self.size)
        lines = wrap_text(self.text, font, self.rect.w - 28)
        line_h = font.get_linesize()
        y = self.rect.centery - (line_h * len(lines)) // 2
        text_color = COLORS["text"] if self.enabled else COLORS["muted"]
        for line in lines:
            img = font.render(line, True, text_color)
            x = self.rect.x + 14 if self.align == "left" else self.rect.centerx - img.get_width() // 2
            surface.blit(img, (x, y))
            y += line_h


class TextInput:
    def __init__(self, rect, max_len=16, text=""):
        self.rect = pygame.Rect(rect)
        self.max_len = max_len
        self.text = text

    def handle_event(self, event):
        """Retourne True quand l'utilisateur valide avec Entrée."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return True
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode and event.unicode.isprintable() and len(self.text) < self.max_len:
                self.text += event.unicode
        return False

    def draw(self, surface, t):
        pygame.draw.rect(surface, COLORS["bg"], self.rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["accent"], self.rect, 2, border_radius=8)
        shown = self.text + ("_" if int(t * 2) % 2 == 0 else " ")
        draw_text(surface, shown, 40, COLORS["text"], (self.rect.x + 16, self.rect.centery), "midleft")


class Background:
    """Pluie de 0 et de 1 façon « matrix », discrète."""

    def __init__(self, width, height):
        rng = random.Random(7)
        self.height = height
        self.time = 0.0
        self.cols = [
            [x, rng.uniform(0, height), rng.uniform(40, 110), rng.randint(5, 11)]
            for x in range(10, width, 26)
        ]
        font = get_font(20)
        self.glyphs = {}
        for ch in "01":
            for level in range(6):
                img = font.render(ch, True, COLORS["accent"])
                img.set_alpha(14 + level * 9)
                self.glyphs[(ch, level)] = img

    def update(self, dt):
        self.time += dt
        for col in self.cols:
            col[1] = (col[1] + col[2] * dt) % (self.height + 200)

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        for i, (x, y, _speed, length) in enumerate(self.cols):
            for k in range(length):
                level = 5 - int(5 * k / length)
                ch = "01"[(int(self.time * 2) + k + i) % 2]
                surface.blit(self.glyphs[(ch, level)], (x, y - k * 18 - 100))
