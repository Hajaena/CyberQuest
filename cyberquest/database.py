"""Tableau d'honneur : stockage SQLite (nom, score, niveau, date)."""
import sqlite3
from contextlib import closing
from datetime import datetime

from .settings import DB_PATH


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(_connect()) as conn, conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS scores (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nom TEXT NOT NULL,
                   score INTEGER NOT NULL,
                   niveau INTEGER NOT NULL DEFAULT 1,
                   date TEXT NOT NULL
               )"""
        )


def add_score(nom, score, niveau):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO scores (nom, score, niveau, date) VALUES (?, ?, ?, ?)",
            (nom, int(score), int(niveau), date),
        )


def top_scores(limit=10):
    """Retourne [(nom, score, niveau, date), ...] trié par score décroissant."""
    with closing(_connect()) as conn:
        return conn.execute(
            "SELECT nom, score, niveau, date FROM scores "
            "ORDER BY score DESC, date ASC LIMIT ?",
            (limit,),
        ).fetchall()


def rank_of(score):
    """Classement (1 = meilleur) d'un score dans le tableau d'honneur."""
    with closing(_connect()) as conn:
        (better,) = conn.execute(
            "SELECT COUNT(*) FROM scores WHERE score > ?", (int(score),)
        ).fetchone()
    return better + 1
