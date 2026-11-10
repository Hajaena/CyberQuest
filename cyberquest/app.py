"""Application : fenêtre, boucle principale et gestion des scènes."""
import pygame

from . import database
from .audio import AudioManager
from .questions import load_questions
from .scenes import (GameScene, LeaderboardScene, MenuScene, NameInputScene,
                     OptionsScene, ResultsScene)
from .settings import FPS, HEIGHT, TITLE, WIDTH, load_config
from .ui import Background


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.cfg = load_config()
        database.init_db()
        self.questions = load_questions()
        self.audio = AudioManager(self.cfg)
        self.background = Background(WIDTH, HEIGHT)
        self.player_name = ""

        self.scenes = {
            "menu": MenuScene(self),
            "name_input": NameInputScene(self),
            "game": GameScene(self),
            "results": ResultsScene(self),
            "leaderboard": LeaderboardScene(self),
            "options": OptionsScene(self),
        }
        self.scene = None
        self.change_scene("menu")
        self.audio.start_music()

    def change_scene(self, name, **kwargs):
        self.scene = self.scenes[name]
        self.scene.on_enter(**kwargs)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)
            self.background.update(dt)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
