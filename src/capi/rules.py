"""Moteur de règles de validation (US-02, US-03, US-04)

Reçoit les cartes d'un tour, une règle et le numéro du tour,
et répond "validé avec telle valeur" ou "revote".
Ajouter une règle = écrire une nouvelle sous-classe de "Rule", sans toucher aux autres
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    """Résultat d'un tour : ``validated`` et, si validé, la carte retenue (sinon ``None``)."""

    validated: bool
    value: str | None = None


class Rule(ABC):
    """Une règle de validation, appliquée à partir du deuxième tour."""

    @abstractmethod
    def decide(self, votes: Sequence[str]) -> Decision:
        """Décide à partir des cartes révélées (ex. ``["5", "5", "8"]``)."""

_CARD_VALUES = {
    "0": 0,
    "1/2": 0.5,
    "1": 1,
    "2": 2,
    "3": 3,
    "5": 5,
    "8": 8,
    "13": 13,
    "20": 20,
    "40": 40,
    "100": 100,
}

_ORDERED_CARDS = ("0", "1/2", "1", "2", "3", "5", "8", "13", "20", "40", "100")

class StrictRule(Rule):
    """Validé seulement si toutes les cartes sont identiques."""

    def decide(self, votes: Sequence[str]) -> Decision:
        if not votes:
            return Decision(validated=False)

        if any(card in {"?", "café"} for card in votes):
            return Decision(validated=False)

        if len(set(votes)) == 1:
            return Decision(validated=True, value=votes[0])

        return Decision(validated=False)


class MedianRule(Rule):
    """Validé à la médiane des cartes ; arrondie à la carte supérieure si besoin."""

    def decide(self, votes: Sequence[str]) -> Decision:
        if not votes:
            return Decision(validated=False)

        if any(card in {"?", "café"} for card in votes):
            return Decision(validated=False)

        values = [_CARD_VALUES[card] for card in votes if card in _CARD_VALUES]

        if len(values) != len(votes):
            return Decision(validated=False)

        values.sort()

        middle = len(values) // 2
        if len(values) % 2 == 1:
            median = values[middle]
        else:
            median = (values[middle - 1] + values[middle]) / 2

        for card in _ORDERED_CARDS:
            if _CARD_VALUES[card] >= median:
                return Decision(validated=True, value=card)

        return Decision(validated=False)


def evaluate(votes: Sequence[str], rule: Rule, round_number: int) -> Decision:
    """Décide du tour.

    Le premier tour impose toujours l'unanimité, quelle que soit la règle.
    """

    if not votes:
        return Decision(validated=False)

    if round_number <= 1:
        if any(card in {"?", "café"} for card in votes):
            return Decision(validated=False)

        if len(set(votes)) == 1:
            return Decision(validated=True, value=votes[0])

        return Decision(validated=False)

    return rule.decide(votes)
