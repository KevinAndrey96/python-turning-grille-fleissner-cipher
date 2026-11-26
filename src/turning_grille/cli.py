"""Command line interface: encrypt, decrypt, generate and search."""

from __future__ import annotations

import argparse
import random
import sys
from collections.abc import Sequence
from typing import TextIO

from turning_grille.attack import SearchSpaceError, search
from turning_grille.cipher import CiphertextLengthError, decrypt, encrypt
from turning_grille.grille import Direction, Grille, GrilleError

DIRECTIONS = {"cw": Direction.CLOCKWISE, "ccw": Direction.COUNTERCLOCKWISE}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="turning-grille", description="Cifrado por rejilla giratoria de Fleissner."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name, summary in (("encrypt", "cifrar"), ("decrypt", "descifrar")):
        command = commands.add_parser(name, help=summary)
        command.add_argument(
            "--grille", "-g", required=True, help='filas separadas por "/", O marca un agujero'
        )
        command.add_argument("--direction", "-d", choices=list(DIRECTIONS), default="cw")
        command.add_argument("text", nargs="?", help="texto; si se omite se lee de stdin")
    generate = commands.add_parser("generate", help="crear una rejilla válida al azar")
    generate.add_argument("--size", "-n", type=int, required=True)
    generate.add_argument("--seed", type=int, help="semilla para obtener siempre la misma")
    finder = commands.add_parser("search", help="probar todas las rejillas de un tamaño")
    finder.add_argument("--size", "-n", type=int, required=True)
    finder.add_argument("--crib", "-c", required=True, help="palabra que se sabe que aparece")
    finder.add_argument("text", help="texto cifrado")

    return parser


def _drawing(grille: Grille) -> str:
    return str(grille).replace("\n", "/")


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
) -> int:
    arguments = _parser().parse_args(argv)
    target = stdout or sys.stdout
    try:
        if arguments.command == "generate":
            rng = (
                random.Random(arguments.seed)
                if arguments.seed is not None
                else random.SystemRandom()
            )
            target.write(f"{_drawing(Grille.random(arguments.size, rng))}\n")
        elif arguments.command == "search":
            for found in search(arguments.text, arguments.size, arguments.crib):
                target.write(f"{_drawing(found.grille)} {found.direction}: {found.plaintext}\n")
        else:
            grille = Grille.parse(arguments.grille.split("/"))
            text = arguments.text if arguments.text is not None else (stdin or sys.stdin).read()
            operation = encrypt if arguments.command == "encrypt" else decrypt
            target.write(operation(text, grille, DIRECTIONS[arguments.direction]) + "\n")
    except (GrilleError, CiphertextLengthError, SearchSpaceError) as error:
        print(f"error: {error}", file=sys.stderr)

        return 2

    return 0
