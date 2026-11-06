"""Chargement et validation d'un backlog JSON (US-01). Logique pure, sans interface."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class BacklogError(Exception):
    """Le backlog ne peut pas être chargé (le message est destiné à l'utilisateur)."""


@dataclass(frozen=True)
class Feature:
    id: str
    titre: str


@dataclass(frozen=True)
class Backlog:
    projet: str
    fonctionnalites: tuple[Feature, ...]

    @property
    def first(self) -> Feature:
        return self.fonctionnalites[0]


def load_backlog(path: str | Path) -> Backlog:
    """Lit un fichier JSON et renvoie le backlog, ou lève BacklogError."""
    p = Path(path)
    try:
        # tolère le BOM ajouté par certains éditeurs Windows.
        text = p.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise BacklogError(f"Fichier introuvable : {p}") from None
    except (OSError, UnicodeDecodeError) as err:
        raise BacklogError(f"Fichier illisible : {p} ({err})") from None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise BacklogError(
            f"JSON invalide dans {p} : {err.msg} (ligne {err.lineno}, colonne {err.colno})."
        ) from None
    return parse_backlog(data)


def _clean(value: object) -> str | None:
    """Texte sans espaces autour, ou None si la valeur n'est pas un texte non vide."""
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def parse_backlog(data: object) -> Backlog:
    """Valide la structure d'un backlog déjà décodé, ou lève BacklogError."""
    if not isinstance(data, dict):
        raise BacklogError("Backlog invalide : la racine du fichier doit être un objet JSON.")

    projet = _clean(data.get("projet"))
    if projet is None:
        raise BacklogError("Backlog invalide : la clé « projet » doit être un texte non vide.")

    items = data.get("fonctionnalites")
    if not isinstance(items, list):
        raise BacklogError("Backlog invalide : la clé « fonctionnalites » doit être une liste.")
    if not items:
        raise BacklogError("Backlog vide : aucune fonctionnalité à estimer.")

    features: list[Feature] = []
    seen: set[str] = set()
    for position, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise BacklogError(f"Backlog invalide : la fonctionnalité n°{position} doit être un objet.")
        fid, titre = _clean(item.get("id")), _clean(item.get("titre"))
        if fid is None:
            raise BacklogError(f"Backlog invalide : la fonctionnalité n°{position} n'a pas d'« id » valide.")
        if titre is None:
            raise BacklogError(f"Backlog invalide : la fonctionnalité « {fid} » n'a pas de « titre » valide.")
        if fid in seen:
            raise BacklogError(f"Backlog invalide : l'identifiant « {fid} » apparaît deux fois.")
        seen.add(fid)
        features.append(Feature(id=fid, titre=titre))

    return Backlog(projet=projet, fonctionnalites=tuple(features))
