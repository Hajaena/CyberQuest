"""Classe de base d'une scène."""


class Scene:
    def __init__(self, app):
        self.app = app

    def on_enter(self, **kwargs):
        """Appelée à chaque affichage de la scène."""

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
