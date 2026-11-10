# CyberQuest : Le Gardien du Réseau

Jeu de sensibilisation à la cybersécurité en **Python / Pygame**.
Tu incarnes un(e) nouvel(le) employé(e) de l'entreprise fictive *NovaTech* et tu montes
d'étage en étage, de l'accueil jusqu'au bureau de la direction. Le hacker **Glitch** avance
à chaque mauvaise réponse : si la jauge de sécurité tombe à zéro, il pirate l'entreprise.

## Installation

```bash
python -m venv venv
# Windows : venv\Scripts\activate      Linux/macOS : source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Python 3.9 ou plus récent.

## Commandes

| Action | Souris | Clavier |
|---|---|---|
| Choisir une réponse | clic | `1` `2` `3` `4` |
| Continuer | bouton « Continuer » | `Entrée` / `Espace` |
| Menu | clic | `↑` `↓` + `Entrée` |
| Retour au menu | | `Échap` |

## Écrans

1. **Menu principal** : Jouer, Tableau d'honneur, Options, Quitter
2. **Saisie du nom**
3. **Jeu** : immeuble, personnage, Glitch, question, jauge de sécurité, score, chronomètre
4. **Résultats** : score, niveau atteint, taux de bonnes réponses, bouton « Générer mon attestation »
5. **Tableau d'honneur** : top 10 (nom, score, étage, date) stocké en SQLite

## Niveaux

| Niveau | Étage | Thème |
|---|---|---|
| 1 | Accueil | Mots de passe & sessions |
| 2 | Open space | E-mails suspects & phishing |
| 3 | Salle serveur | Sécurité physique & sauvegardes |
| 4 | Direction | Boss final : le grand mélange |

40 questions au total (10 par niveau). Des mini-événements visuels illustrent certaines
questions : faux e-mail, clé USB, visiteur sans badge, appel suspect, cadenas, serveurs.

## Score

- **100 points** par bonne réponse
- **bonus de rapidité** : jusqu'à +50 selon le temps restant
- **bonus de série** : +10 par bonne réponse consécutive (plafond +50)
- **bonus d'étage** : +200 points à chaque étage terminé
- Mauvaise réponse ou temps écoulé : −20 de sécurité et série remise à zéro
- Bonne réponse : +5 de sécurité

## Personnaliser le jeu

### `config.json`

```json
{
  "company_name": "NovaTech",
  "question_time_seconds": 20,
  "questions_per_level": 10,
  "security_max": 100,
  "security_penalty": 20,
  "security_heal": 5,
  "music_enabled": true,
  "sfx_enabled": true,
  "volume": 0.5
}
```

- `company_name` : nom de l'entreprise (menu, enseigne, attestation)
- `question_time_seconds` : durée du chronomètre, `0` pour le désactiver
- les options sonores et la durée sont aussi modifiables depuis l'écran **Options**

### `data/questions.json`

Chaque question suit ce format (4 choix maximum, `bonne_reponse` = index à partir de 0) :

```json
{
  "niveau": 1,
  "theme": "Mots de passe & sessions",
  "question": "Quel mot de passe est le plus sûr ?",
  "choix": ["Azerty123", "Fatima2024", "Tr0ub4dor&3-Cafe!", "motdepasse"],
  "bonne_reponse": 2,
  "explication": "Une phrase longue mélangeant majuscules, chiffres et symboles résiste mieux.",
  "evenement": "cadenas"
}
```

`evenement` est facultatif : `email`, `usb`, `visiteur`, `telephone`, `cadenas` ou `serveur`.
Les choix sont mélangés à chaque partie. Le fichier est validé au démarrage.

## Structure du projet

```
CyberQuest/
├── main.py                  # point d'entrée
├── requirements.txt
├── config.json              # réglages modifiables
├── data/
│   ├── questions.json       # contenu pédagogique
│   └── scores.db            # créé au premier lancement (SQLite)
├── assets/sounds/           # sons 8-bit (.wav), régénérés si absents
├── attestations/            # PDF générés
├── tools/
│   └── generate_sounds.py   # régénère les sons
└── cyberquest/
    ├── app.py               # fenêtre, boucle principale, scènes
    ├── settings.py          # chemins, couleurs, niveaux, score, config
    ├── database.py          # SQLite : tableau d'honneur
    ├── questions.py         # chargement / tirage des questions
    ├── audio.py             # effets sonores et musique
    ├── soundgen.py          # synthèse des sons chiptune
    ├── certificate.py       # attestation PDF (reportlab)
    ├── ui.py                # boutons, textes, saisie, fond animé
    ├── sprites.py           # immeuble, personnages, mini-événements
    └── scenes/
        ├── menu.py · name_input.py · game.py
        └── results.py · leaderboard.py · options.py
```

Répartition d'équipe possible : moteur de jeu (`scenes/game.py`), interface (`ui.py`, `sprites.py`),
contenu (`questions.json`), audio + PDF (`audio.py`, `soundgen.py`, `certificate.py`), base de données (`database.py`).
# CyberQuest
