"""Moteur de partie : configuration des joueurs et vote caché (US-01, US-06).

L'interface appelle ces fonctions et affiche les erreurs.
La validation (règle stricte, médiane...) n'est pas dans ce sprint.
"""

from __future__ import annotations
from collections.abc import Iterable
from .backlog import Backlog, Feature

CARDS: tuple[str, ...] = ("0", "1/2", "1", "2", "3", "5", "8", "13", "20", "40", "100", "?", "café")
MIN_PLAYERS = 2

# Saisie insensible à la casse, et « cafe » sans accent accepté.
_CARD_LOOKUP = {card.lower(): card for card in CARDS} | {"cafe": "café"}


class ConfigError(ValueError):
    """Configuration de partie refusée (indique la valeur refusée)."""


class VoteError(ValueError):
    """Vote refusé (indique la raison)."""


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


def parse_card(raw: str) -> str:
    card = _CARD_LOOKUP.get(raw.strip().lower())
    if card is None:
        raise VoteError(f"Carte refusée : « {raw.strip()} ». Cartes valables : {', '.join(CARDS)}.")
    return card


class Game:
    """Une partie : des joueurs, un backlog, et les votes du tour en cours."""

    def __init__(self, players: Iterable[str], backlog: Backlog) -> None:
        pseudos: list[str] = []
        for raw in players:
            pseudos.append(validate_pseudo(raw, pseudos))
        if len(pseudos) < MIN_PLAYERS:
            raise ConfigError(f"Nombre de joueurs refusé : {len(pseudos)} (minimum {MIN_PLAYERS}).")
        self._players = tuple(pseudos)
        self._backlog = backlog
        self._votes: dict[str, str] = {}
        self._revealed = False

    @property
    def players(self) -> tuple[str, ...]:
        return self._players

    @property
    def backlog(self) -> Backlog:
        return self._backlog

    @property
    def current_feature(self) -> Feature:
        return self._backlog.first

    @property
    def pending(self) -> tuple[str, ...]:
        """Joueurs qui n'ont pas encore voté (leur carte n'est jamais exposée)."""
        return tuple(p for p in self._players if p not in self._votes)

    def cast_vote(self, player: str, raw_card: str) -> None:
        if self._revealed:
            raise VoteError("Les cartes sont déjà révélées.")
        if player not in self._players:
            raise VoteError(f"Joueur inconnu : « {player} ».")
        if player in self._votes:
            raise VoteError(f"{player} a déjà voté.")
        self._votes[player] = parse_card(raw_card)

    def reveal(self) -> dict[str, str]:
        """Révèle toutes les cartes ensemble. Impossible tant qu'un joueur n'a pas voté."""
        if self.pending:
            raise VoteError(f"Votes manquants : {', '.join(self.pending)}.")
        self._revealed = True
        return {player: self._votes[player] for player in self._players}
