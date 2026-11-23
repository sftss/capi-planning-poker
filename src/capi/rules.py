"""Moteur de règles de validation (US-02, US-03, US-04)

Reçoit les cartes d'un tour, une règle et le numéro du tour,
et répond "validé avec telle valeur" ou "revote".
Ajouter une règle = écrire une nouvelle sous-classe de "Rule", sans toucher aux autres
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import median


@dataclass(frozen=True)
class Decision:
    """Résultat d'un tour : ``validated`` et, si valid la carte retenue (sinon ``None``)"""

    validated: bool
    value: str | None = None


class Rule(ABC):
    """Règle de validation, appliquée à partir du deuxième tour"""

    # Nom écrit dans l'export et la sauvegarde JSON
    name: str = ""

    @abstractmethod
    def decide(self, votes: Sequence[str]) -> Decision:
        """Décide à partir des cartes révélées (ex. ``["5", "5", "8"]``)"""


# Cartes numériques, dans l'ordre croissant ("?" et "café" n'en font pas partie)
_CARD_VALUES = {"0": 0, "1/2": 0.5, "1": 1, "2": 2, "3": 3, "5": 5, "8": 8, "13": 13, "20": 20, "40": 40, "100": 100}


class StrictRule(Rule):
    """Validé seulement si toutes les cartes sont identiques (et numériques)"""

    name = "strict"

    def decide(self, votes: Sequence[str]) -> Decision:
        if votes and len(set(votes)) == 1 and votes[0] in _CARD_VALUES:
            return Decision(validated=True, value=votes[0])
        return Decision(validated=False)


class MedianRule(Rule):
    """Validé à la médiane des cartes ; arrondie à la carte supérieure si besoin"""

    name = "mediane"

    def decide(self, votes: Sequence[str]) -> Decision:
        if not votes or any(card not in _CARD_VALUES for card in votes):
            return Decision(validated=False)
        mid = median([_CARD_VALUES[card] for card in votes])
        # première carte >= médiane (existe toujours : la médiane ne dépasse pas 100)
        card = next(card for card, value in _CARD_VALUES.items() if value >= mid)
        return Decision(validated=True, value=card)


RULES: dict[str, type[Rule]] = {StrictRule.name: StrictRule, MedianRule.name: MedianRule}


def rule_from_name(name: str) -> Rule:
    """Recrée une règle à partir de son nom ; KeyError si inconnu"""
    return RULES[name]()


def evaluate(votes: Sequence[str], rule: Rule, round_number: int) -> Decision:
    """Décide du tour ; le premier tour impose l'unanimité, quelle que soit la règle"""
    if round_number <= 1:
        return StrictRule().decide(votes)
    return rule.decide(votes)
