"""Interface console. Ne contient aucune règle de jeu : tout passe par ``game`` et ``backlog``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence

from .backlog import Backlog, BacklogError, load_backlog
from .game import ConfigError, Game, parse_player_count, validate_pseudo

DEFAULT_BACKLOG = "exemples/backlog.json"

InputFn = Callable[[str], str]
PrintFn = Callable[..., None]


def configure_players(input_fn: InputFn, print_fn: PrintFn) -> list[str]:
    """Saisie du nombre de joueurs puis des pseudos ; redemande tant que la valeur est refusée."""
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


def load_backlog_interactive(first_path: str | None, input_fn: InputFn, print_fn: PrintFn) -> Backlog | None:
    """Charge le backlog ; en cas d'erreur, affiche le message et redemande. None si abandon."""
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


def main(
    argv: Sequence[str] | None = None,
    input_fn: InputFn = input,
    print_fn: PrintFn = print,
) -> int:
    parser = argparse.ArgumentParser(prog="capi", description="Planning poker en console.")
    parser.add_argument("backlog", nargs="?", help=f"fichier backlog JSON (défaut proposé : {DEFAULT_BACKLOG})")
    args = parser.parse_args(argv)

    try:
        print_fn("=== CAPI : planning poker ===")
        # Le backlog est chargé en premier : un abandon ne fait pas perdre la saisie des joueurs.
        backlog = load_backlog_interactive(args.backlog, input_fn, print_fn)
        if backlog is None:
            print_fn("Aucune partie créée.")
            return 1

        pseudos = configure_players(input_fn, print_fn)

        game = Game(pseudos, backlog)
        feature = game.current_feature
        print_fn(f"\nProjet : {backlog.projet} ({len(backlog.fonctionnalites)} fonctionnalités)")
        print_fn(f"Fonctionnalité à estimer : {feature.id} : {feature.titre}\n")

        return 0
    except (EOFError, KeyboardInterrupt):
        print_fn("\nPartie abandonnée.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
