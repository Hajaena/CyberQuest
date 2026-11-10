"""Chargement et tirage des questions depuis data/questions.json."""
import json
import random

from .settings import QUESTIONS_PATH

REQUIRED_KEYS = ("niveau", "question", "choix", "bonne_reponse", "explication")


def load_questions(path=QUESTIONS_PATH):
    """Charge et valide le fichier JSON. Lève ValueError si une question est invalide."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("questions", [])

    for i, q in enumerate(data, start=1):
        missing = [k for k in REQUIRED_KEYS if k not in q]
        if missing:
            raise ValueError(f"questions.json, question n°{i} : champs manquants {missing}")
        if not 2 <= len(q["choix"]) <= 4:
            raise ValueError(f"questions.json, question n°{i} : il faut 2 à 4 choix")
        if not 0 <= q["bonne_reponse"] < len(q["choix"]):
            raise ValueError(f"questions.json, question n°{i} : 'bonne_reponse' hors limites")
    return data


def pick_for_level(questions, level, count, shuffle_choices=True):
    """Tire `count` questions du niveau (mélangées, choix mélangés)."""
    pool = [q for q in questions if q["niveau"] == level]
    random.shuffle(pool)
    picked = []
    for q in pool[:count]:
        q = dict(q)
        if shuffle_choices:
            order = list(range(len(q["choix"])))
            random.shuffle(order)
            q["choix"] = [q["choix"][i] for i in order]
            q["bonne_reponse"] = order.index(q["bonne_reponse"])
        picked.append(q)
    return picked
