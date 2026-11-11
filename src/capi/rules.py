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


class StrictRule(Rule):
    """Validé seulement si toutes les cartes sont identiques."""

    def decide(self, votes: Sequence[str]) -> Decision:
        raise NotImplementedError


class MedianRule(Rule):
    """Validé à la médiane des cartes ; arrondie à la carte supérieure si besoin."""

    def decide(self, votes: Sequence[str]) -> Decision:
        raise NotImplementedError


def evaluate(votes: Sequence[str], rule: Rule, round_number: int) -> Decision:
    """Décision du tour ``round_number`` (1 = premier tour, toujours à l'unanimité)."""
    raise NotImplementedError
