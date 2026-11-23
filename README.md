# capi-planning-poker

[![CI](https://github.com/sftss/capi-planning-poker/actions/workflows/ci.yml/badge.svg)](https://github.com/sftss/capi-planning-poker/actions/workflows/ci.yml)

CAPI : application de planning poker en console (projet de Conception agile, binôme B2-11).

État actuel (sprint 2) : saisie des joueurs, chargement d'un backlog JSON, vote caché puis révélation des cartes, validation selon la règle choisie (stricte ou médiane, premier tour toujours à l'unanimité), export JSON des estimations, pause café avec sauvegarde et reprise.

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

Sans argument (`python -m capi`), un menu propose une nouvelle partie (`n`), la reprise d'une partie sauvegardée (`r`) ou de quitter (`q`). Si un fichier (backlog ou sauvegarde) est absent, mal formé ou vide, un message d'erreur s'affiche et le chemin est redemandé (`q` pour abandonner).

Pendant le vote, la carte tapée par chaque joueur n'est pas affichée. Toutes les cartes sont révélées ensemble une fois que tous les joueurs ont voté.

- **Fin du backlog** : les estimations sont exportées dans `estimations.json` (chaque fonctionnalité avec sa difficulté, et la règle choisie) ;
- **Carte café** : si tous les joueurs jouent `café`, la partie est sauvegardée dans `sauvegarde.json` puis l'application s'arrête. Pour reprendre : `python -m capi`, puis `r` ;
- Les deux chemins se changent avec `--export FICHIER` et `--sauvegarde FICHIER`.

## Tests

```bash
pytest
```

La CI (GitHub Actions) lance les tests à chaque push et PR vers `main`, puis génère la documentation du code avec pdoc. En local : `pip install pdoc && pdoc capi -o site`.

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

- `src/capi/backlog.py`, `src/capi/game.py` et `src/capi/rules.py` : logique (backlog, joueurs, votes, règles), sans entrée/sortie ;
- `src/capi/persistence.py` : export des estimations, sauvegarde et reprise d'une partie (conversion JSON) ;
- `src/capi/cli.py` : interface console, sans règle de jeu ;
- `tests/` : tests pytest ;
