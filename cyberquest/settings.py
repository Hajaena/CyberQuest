"""Paramètres globaux, chemins, couleurs et gestion de config.json."""
import json
from pathlib import Path

# --- Chemins -----------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SOUNDS_DIR = ROOT_DIR / "assets" / "sounds"
ATTESTATIONS_DIR = ROOT_DIR / "attestations"
CONFIG_PATH = ROOT_DIR / "config.json"
QUESTIONS_PATH = DATA_DIR / "questions.json"
DB_PATH = DATA_DIR / "scores.db"

# --- Fenêtre -----------------------------------------------------------------
WIDTH, HEIGHT = 960, 600
FPS = 60
TITLE = "CyberQuest : Le Gardien du Réseau"

# --- Couleurs ----------------------------------------------------------------
COLORS = {
    "bg": (10, 14, 30),
    "panel": (22, 30, 56),
    "panel_border": (60, 90, 160),
    "text": (235, 240, 255),
    "muted": (150, 165, 200),
    "accent": (0, 220, 150),
    "danger": (240, 70, 90),
    "warn": (255, 200, 60),
    "button": (36, 52, 96),
    "button_hover": (58, 86, 152),
    "glitch": (190, 60, 255),
    "white": (255, 255, 255),
}

# --- Niveaux (un niveau = un étage) -------------------------------------------
LEVELS = [
    {
        "nom": "Accueil",
        "theme": "Mots de passe & sessions",
        "intro": "Premier jour chez {company} ! Glitch rôde déjà autour du bâtiment. "
                 "Protège les comptes dès l'accueil.",
    },
    {
        "nom": "Open space",
        "theme": "E-mails suspects & phishing",
        "intro": "L'open space est la cible préférée des e-mails piégés. "
                 "Garde l'oeil ouvert avant de cliquer.",
    },
    {
        "nom": "Salle serveur",
        "theme": "Sécurité physique & sauvegardes",
        "intro": "Les serveurs hébergent tout ce que {company} possède. "
                 "Visiteurs, clés USB, sauvegardes : aucune erreur permise.",
    },
    {
        "nom": "Direction",
        "theme": "Boss final : le grand mélange",
        "intro": "Dernier étage ! Glitch joue sa dernière carte. "
                 "Montre que tu mérites le poste de Responsable Sécurité.",
    },
]

# --- Score ---------------------------------------------------------------------
BASE_POINTS = 100        # points par bonne réponse
MAX_TIME_BONUS = 50      # bonus de rapidité maximal
COMBO_STEP = 10          # bonus par bonne réponse consécutive
MAX_COMBO_BONUS = 50     # plafond du bonus de série
LEVEL_BONUS = 200        # bonus à la fin d'un étage

# --- Configuration utilisateur (config.json) -----------------------------------
DEFAULT_CONFIG = {
    "company_name": "NovaTech",
    "question_time_seconds": 20,   # 0 = pas de chronomètre
    "questions_per_level": 10,
    "security_max": 100,
    "security_penalty": 20,        # perte sur mauvaise réponse
    "security_heal": 5,            # gain sur bonne réponse
    "music_enabled": True,
    "sfx_enabled": True,
    "volume": 0.5,
}


def load_config():
    """Charge config.json en complétant avec les valeurs par défaut."""
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg.update(json.load(f))
    except (OSError, json.JSONDecodeError):
        pass
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
