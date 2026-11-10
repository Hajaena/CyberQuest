"""Régénère tous les sons 8-bit dans assets/sounds/ : python tools/generate_sounds.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cyberquest.settings import SOUNDS_DIR  # noqa: E402
from cyberquest.soundgen import ensure_sounds  # noqa: E402

if __name__ == "__main__":
    ensure_sounds(SOUNDS_DIR, force=True)
    print(f"Sons générés dans {SOUNDS_DIR}")
