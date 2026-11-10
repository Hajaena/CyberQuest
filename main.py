"""Point d'entrée de CyberQuest : python main.py"""
import json
import sys

from cyberquest.app import App


def main():
    try:
        app = App()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Erreur au démarrage : {exc}")
        sys.exit(1)
    app.run()


if __name__ == "__main__":
    main()
