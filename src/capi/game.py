"""Moteur de partie : configuration des joueurs (US-01).

L'interface appelle ces fonctions et affiche les erreurs.
La validation (règle stricte, médiane...) n'est pas dans ce sprint.
"""

from __future__ import annotations
from collections.abc import Iterable
from .backlog import Backlog, Feature

MIN_PLAYERS = 2

class ConfigError(ValueError):
    """Configuration de partie refusée (indique la valeur refusée)."""


def parse_player_count(raw: str) -> int:
    try:
        count = int(raw.strip())
    except ValueError:
        raise ConfigError(f"Nombre de joueurs refusé : « {raw.strip()} » n'est pas un nombre entier.") from None
    if count < MIN_PLAYERS:
        raise ConfigError(f"Nombre de joueurs refusé : {count} (minimum {MIN_PLAYERS}).")
    return count


def validate_pseudo(raw: str, existing: Iterable[str]) -> str:
    """Renvoie le pseudo nettoyé. Deux pseudos ne diffèrent pas seulement par la casse."""
    pseudo = raw.strip()
    if not pseudo:
        raise ConfigError("Pseudo refusé : valeur vide.")
    if pseudo.casefold() in {other.casefold() for other in existing}:
        raise ConfigError(f"Pseudo refusé : « {pseudo} » est déjà pris.")
    return pseudo


class Game:
    """Une partie : des joueurs et un backlog."""

    def __init__(self, players: Iterable[str], backlog: Backlog) -> None:
        pseudos: list[str] = []
        for raw in players:
            pseudos.append(validate_pseudo(raw, pseudos))
        if len(pseudos) < MIN_PLAYERS:
            raise ConfigError(f"Nombre de joueurs refusé : {len(pseudos)} (minimum {MIN_PLAYERS}).")
        self._players = tuple(pseudos)
        self._backlog = backlog

    @property
    def players(self) -> tuple[str, ...]:
        return self._players

    @property
    def backlog(self) -> Backlog:
        return self._backlog

    @property
    def current_feature(self) -> Feature:
        return self._backlog.first
