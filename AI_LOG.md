# AI_LOG.md : journal d'usage de l'IA

> À placer à la racine du dépôt. À remplir **au fil de l'eau**, pas en fin de projet. Une entrée par tâche (pas par message), en 5 lignes.
> Rappel : l'IA est autorisée pour le **code de production** et la **configuration d'outils** uniquement. Qui a fait la demande, les fichiers touchés et les commits se retrouvent dans l'historique Git : ne les recopiez pas.

## Outils utilisés (à remplir une fois)

| Outil | Modèle (si connu) | Mode (autocomplétion, chat, agent) |
|---|---|---|
| Claude (claude.ai, avec accès au dépôt) | Claude Sonnet 5.5 | agent |

Fichier d'instructions pour agent versionné (`CLAUDE.md`, `AGENTS.md`...) : non

## Entrées

### 2026-11-03 : Walking skeleton Python : saisie des joueurs, chargement du backlog, vote caché (US-01, US-06)

- **Demande (résumé fidèle)** : écrire en Python un squelette qui sépare moteur (`backlog.py`, `game.py`) et interface console (`cli.py`) : saisie du nombre de joueurs et des pseudos avec messages d'erreur (CU-01, 1a), chargement backlog JSON avec gestion des erreurs (extension 2a), vote caché puis révélation. Ajout aussi de `pyproject.toml`, `.gitignore` et du README. Contexte fourni : fiche S1, R0.md, énoncé du projet. Aucun test demandé à l'IA.
- **Résultat** : modifié.
- **Ce que nous avons vérifié** : l'IA a lancé le programme avec des entrées simulées (joueur unique, pseudo vide ou en double, fichier absent, backlog vide ou mal formé, abandon). Notre lecture ligne à ligne et notre essai manuel : OK.
- **Ce que nous avons changé ou rejeté, et pourquoi** : reforumation, simplication de certains passsages

### AAAA-MM-JJ : ...

## Bilan (à compléter en séance 4, 3 lignes)

- Nombre d'entrées et de propositions rejetées ou corrigées :
- Tâches où l'IA a fait gagner du temps :
- Tâches où l'IA a fait perdre du temps :
