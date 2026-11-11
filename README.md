# capi-planning-poker

[![CI](https://github.com/sftss/capi-planning-poker/actions/workflows/ci.yml/badge.svg)](https://github.com/sftss/capi-planning-poker/actions/workflows/ci.yml)

CAPI : application de planning poker en console (projet de Conception agile, binôme B2-11).

État actuel (sprint 1) : saisie des joueurs, chargement d'un backlog JSON, vote caché puis révélation des cartes. La validation selon une règle (stricte, médiane...) arrive au sprint 2.

## Prérequis

- Python 3.10 ou plus récent
- Git

## Installation et lancement

Depuis la racine du dépôt, après un `git clone` :

```bash
python -m venv .venv
.venv\Scripts\activate      # Linux/macOS : source .venv/bin/activate
pip install -e ".[dev]"
python -m capi exemples/backlog.json
```

Sans argument (`python -m capi`), l'application demande le chemin du fichier backlog. Si le fichier est absent, mal formé ou vide, un message d'erreur s'affiche et le chemin est redemandé (`q` pour abandonner).

Pendant le vote, la carte tapée par chaque joueur n'est pas affichée. Toutes les cartes sont révélées ensemble une fois que tous les joueurs ont voté.

## Tests

A venir 

## Format du backlog JSON

Structure du sujet ici :

```json
{
  "projet": "Bibliothèque en ligne",
  "fonctionnalites": [
    { "id": "F1", "titre": "Rechercher un livre par titre" },
    { "id": "F2", "titre": "Emprunter un livre disponible" }
  ]
}
```

- `projet` : texte non vide ;
- `fonctionnalites` : liste non vide ; chaque élément a un `id` unique et un `titre`, tous deux non vides ;
- Exemple complet dans `exemples/backlog.json` ;

## Organisation du code

- `src/capi/backlog.py` et `src/capi/game.py` : logique (backlog, joueurs, votes), sans entrée/sortie ;
- `src/capi/cli.py` : interface console, sans règle de jeu ;
- `tests/` : tests pytest (voir la section « Tests ») ;
