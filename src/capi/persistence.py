"""Export des estimations (US-05) et sauvegarde / reprise d'une partie (carte café)

Logique, conversion entre Game et JSON sans interface
"""

from __future__ import annotations

import json
from pathlib import Path

from .backlog import BacklogError, parse_backlog
from .game import ConfigError, Game
from .rules import RULES, rule_from_name

SAVE_VERSION = 1


class SaveError(Exception):
    """La sauvegarde ne peut pas être lue (renvoyer message à l'utilisateur)"""


def export_results(game: Game) -> dict:
    """Résultat final chaque fonctionnalité avec sa difficulté estimée et la règle choisie"""
    estimates = game.estimates
    return {
        "projet": game.backlog.projet,
        "regle": game.rule.name,
        "fonctionnalites": [
            {"id": f.id, "titre": f.titre, "difficulte": estimates.get(f.id)}
            for f in game.backlog.fonctionnalites
        ],
    }


def game_to_state(game: Game) -> dict:
    """État complet de la partie, pour la reprendre plus tard."""
    return {
        "version": SAVE_VERSION,
        "joueurs": list(game.players),
        "regle": game.rule.name,
        "backlog": {
            "projet": game.backlog.projet,
            "fonctionnalites": [{"id": f.id, "titre": f.titre} for f in game.backlog.fonctionnalites],
        },
        "estimations": game.estimates,
        "fonctionnalite_courante": game.current_feature.id,
    }


def game_from_state(data: object) -> Game:
    """Recrée la partie depuis un état sauvegardé, ou lève SaveError."""
    if not isinstance(data, dict):
        raise SaveError("Sauvegarde invalide : la racine du fichier doit être un objet JSON")
    if data.get("version") != SAVE_VERSION:
        raise SaveError(f"Sauvegarde invalide : version '{data.get('version')}' non prise en charge")

    rule_name = data.get("regle")
    if rule_name not in RULES:
        raise SaveError(f"Sauvegarde invalide : règle '{rule_name}' inconnue")

    players = data.get("joueurs")
    if not isinstance(players, list) or not all(isinstance(p, str) for p in players):
        raise SaveError("Sauvegarde invalide : 'joueurs' doit être une liste de pseudos")

    estimates = data.get("estimations")
    if not isinstance(estimates, dict) or not all(isinstance(v, str) for v in estimates.values()):
        raise SaveError("Sauvegarde invalide : 'estimations' doit associer un id à une carte")

    current = data.get("fonctionnalite_courante")
    if not isinstance(current, str):
        raise SaveError("Sauvegarde invalide : 'fonctionnalite_courante' manquante")

    try:
        backlog = parse_backlog(data.get("backlog"))
        return Game(
            players,
            backlog,
            rule_from_name(rule_name),
            estimates=estimates,
            current_feature_id=current,
        )
    except (BacklogError, ConfigError) as err:
        raise SaveError(f"Sauvegarde invalide : {err}") from None


def write_json(data: dict, path: str | Path) -> None:
    """Écrit un dictionnaire en JSON lisible (UTF-8, accents conservés)."""
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_game(game: Game, path: str | Path) -> None:
    """Sauvegarde la partie dans un fichier JSON."""
    write_json(game_to_state(game), path)


def load_game(path: str | Path) -> Game:
    """Charge une sauvegarde, ou lève SaveError."""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise SaveError(f"Fichier introuvable : {p}") from None
    except (OSError, UnicodeDecodeError) as err:
        raise SaveError(f"Fichier illisible : {p} ({err})") from None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise SaveError(f"JSON invalide dans {p} : {err.msg} (ligne {err.lineno})") from None
    return game_from_state(data)
