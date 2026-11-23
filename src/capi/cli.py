"""Interface console, contient aucune règle de jeu : tout passe par game, backlog et persistence"""

from __future__ import annotations

import argparse, getpass, sys
from collections.abc import Callable, Sequence
from enum import Enum

from .backlog import Backlog, BacklogError, load_backlog
from .game import CARDS, ConfigError, Game, VoteError, parse_player_count, validate_pseudo
from .persistence import SaveError, export_results, load_game, save_game, write_json
from .rules import MedianRule, Rule, StrictRule

DEFAULT_BACKLOG = "exemples/backlog.json"
DEFAULT_SAVE = "sauvegarde.json"
DEFAULT_EXPORT = "estimations.json"

# Injection de dépendances => n'appelle jamais input(), getpass() ou print()
# directement, elle reçoit ces fonctions en paramètre (input_fn, secret_fn, print_fn).
# main() utilise les valeurs par défaut (clavier / terminal). Dans un test,
# on passe des fonctions qui renvoient des réponses
InputFn = Callable[[str], str] # reçoit la question, renvoie la réponse
PrintFn = Callable[..., None] # même signature que print


class RoundOutcome(Enum):
    VALIDATED = "validé"
    REVOTE = "revote"
    COFFEE = "café"


def configure_players(input_fn: InputFn, print_fn: PrintFn) -> list[str]:
    """Saisie du nombre de joueurs puis des pseudos ; redemande si refusé"""
    while True:
        try:
            count = parse_player_count(input_fn("Nombre de joueurs : "))
            break
        except ConfigError as err:
            print_fn(err)

    pseudos: list[str] = []
    while len(pseudos) < count:
        try:
            pseudos.append(validate_pseudo(input_fn(f"Pseudo du joueur {len(pseudos) + 1} : "), pseudos))
        except ConfigError as err:
            print_fn(err)
    return pseudos


def configure_rule(input_fn: InputFn, print_fn: PrintFn) -> Rule:
    """Demande la règle de validation"""
    while True:
        choice = input_fn("Règle de validation (strict / mediane) : ").strip().lower()

        if choice in {"strict", "stricte"}:
            return StrictRule()

        if choice in {"mediane", "median", "médiane"}:
            return MedianRule()

        print_fn("Règle refusée")


def load_backlog_interactive(first_path: str | None, input_fn: InputFn, print_fn: PrintFn) -> Backlog | None:
    """Charge le backlog ; si erreur affiche le message et redemande, None si abandon"""
    path = first_path
    while True:
        if path is None:
            answer = input_fn(f"Fichier backlog JSON (q pour abandonner) [{DEFAULT_BACKLOG}] : ").strip()
            if answer.lower() == "q":
                return None
            path = answer or DEFAULT_BACKLOG
        try:
            return load_backlog(path)
        except BacklogError as err:
            print_fn(err)
            path = None


def load_save_interactive(input_fn: InputFn, print_fn: PrintFn) -> Game | None:
    """Charge une sauvegarde (2b) ; redemande si erreur, None si abandon"""
    while True:
        answer = input_fn(f"Fichier de sauvegarde (q pour abandonner) [{DEFAULT_SAVE}] : ").strip()
        if answer.lower() == "q":
            return None
        try:
            return load_game(answer or DEFAULT_SAVE)
        except SaveError as err:
            print_fn(err)


def new_game(backlog_path: str | None, input_fn: InputFn, print_fn: PrintFn) -> Game | None:
    """Configure une nouvelle parti, None si Scrum Master abandonne"""
    # backlog est chargé en premier
    backlog = load_backlog_interactive(backlog_path, input_fn, print_fn)
    if backlog is None:
        return None
    pseudos = configure_players(input_fn, print_fn)
    rule = configure_rule(input_fn, print_fn)
    return Game(pseudos, backlog, rule)


def choose_start(input_fn: InputFn, print_fn: PrintFn) -> str:
    """Menu de départ : "n" (nouvelle partie), "r" (reprise) ou "q" (quitter)"""
    while True:
        choice = input_fn("[n] Nouvelle partie  [r] Reprendre une partie  [q] Quitter : ")
        choice = choice.strip().lower()
        if choice in {"n", "r", "q"}:
            return choice
        print_fn("Choix refusé : saisissez n, r ou q")


def run_votes(game: Game, secret_fn: InputFn, print_fn: PrintFn) -> dict[str, str]:
    """Chaque joueur vote à son tour sans que sa carte soit affichée, puis révélation"""
    cards = ", ".join(CARDS)
    for player in game.players:
        while True:
            try:
                game.cast_vote(player, secret_fn(f"{player}, votre carte ({cards}) : "))
                break
            except VoteError as err:
                print_fn(err)
    return game.reveal()


def play_round(game: Game, secret_fn: InputFn, print_fn: PrintFn) -> RoundOutcome:
    """Joue un tour : validation, revote, ou pause café si tout le monde a joué café"""
    print_fn(f"\n--- Tour {game.round_number} ---")

    votes = run_votes(game, secret_fn, print_fn)
    print_fn("\nCartes révélées :")
    for player, card in votes.items():
        print_fn(f"  {player} : {card}")

    if game.is_coffee_break:
        return RoundOutcome.COFFEE

    decision = game.decide()
    if decision.validated:
        print_fn(f"\nFonctionnalité validée avec la valeur {decision.value}")
        return RoundOutcome.VALIDATED

    print_fn("\nPas d'accord : un nouveau tour commence")
    game.start_next_round()
    return RoundOutcome.REVOTE


def play_game(game: Game, secret_fn: InputFn, print_fn: PrintFn, save_path: str, export_path: str) -> int:
    """Enchaîne jusqu'à l'export final ou la pause café"""
    print_fn(
        f"\nProjet : {game.backlog.projet} ({len(game.backlog.fonctionnalites)} fonctionnalités, "
        f"règle {game.rule.name}, {len(game.estimates)} déjà estimée(s))"
    )
    while True:
        feature = game.current_feature
        print_fn(f"\nFonctionnalité à estimer : {feature.id} : {feature.titre}")

        outcome = play_round(game, secret_fn, print_fn)
        while outcome is RoundOutcome.REVOTE:
            outcome = play_round(game, secret_fn, print_fn)

        if outcome is RoundOutcome.COFFEE:
            save_game(game, save_path)
            print_fn(f"\nPause café : partie sauvegardée dans {save_path}. Reprise via le menu [r]")
            return 0

        if not game.has_next_feature:
            write_json(export_results(game), export_path)
            print_fn(f"\nToutes les fonctionnalités ont été estimées. Résultats exportés dans {export_path}")
            return 0
        game.next_feature()


def main(
    argv: Sequence[str] | None = None,
    input_fn: InputFn = input,
    secret_fn: InputFn = getpass.getpass,
    print_fn: PrintFn = print,
) -> int:
    parser = argparse.ArgumentParser(prog="capi", description="Planning poker en console")
    parser.add_argument(
        "backlog", nargs="?", help="fichier backlog JSON : lance directement une nouvelle partie"
    )
    parser.add_argument("--sauvegarde", default=DEFAULT_SAVE, help=f"fichier écrit à la pause café (défaut : {DEFAULT_SAVE})")
    parser.add_argument("--export", default=DEFAULT_EXPORT, help=f"fichier des résultats (défaut : {DEFAULT_EXPORT})")
    args = parser.parse_args(argv)

    try:
        print_fn("=== CAPI : planning poker ===")
        choice = "n" if args.backlog else choose_start(input_fn, print_fn)
        if choice == "q":
            return 0
        if choice == "r":
            game = load_save_interactive(input_fn, print_fn)
        else:
            game = new_game(args.backlog, input_fn, print_fn)
        if game is None:
            print_fn("Aucune partie créée")
            return 1
        return play_game(game, secret_fn, print_fn, args.sauvegarde, args.export)
    except (EOFError, KeyboardInterrupt):
        print_fn("\nPartie abandonnée")
        return 1


if __name__ == "__main__":
    sys.exit(main())