"""Scènes du jeu (une classe par écran)."""
from .game import GameScene
from .leaderboard import LeaderboardScene
from .menu import MenuScene
from .name_input import NameInputScene
from .options import OptionsScene
from .results import ResultsScene

__all__ = [
    "GameScene",
    "LeaderboardScene",
    "MenuScene",
    "NameInputScene",
    "OptionsScene",
    "ResultsScene",
]
