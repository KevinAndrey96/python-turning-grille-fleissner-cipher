"""Transposition with a turning grille: write through the holes, turn, repeat,
then read the grid row by row."""

from __future__ import annotations

import unicodedata

from turning_grille.grille import Cell, Direction, Grille

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
FILLER = "X"


class CiphertextLengthError(ValueError):
    """Raised when a ciphertext does not fill whole grids."""


def normalize(text: str) -> str:
    """Uppercase letters only, with accents removed (á -> A, ñ -> N)."""
    decomposed = unicodedata.normalize("NFD", text.upper())

    return "".join(char for char in decomposed if char in ALPHABET)


def reading_order(grille: Grille) -> list[Cell]:
    """Grid cells row by row, skipping an odd center that no hole uses."""
    used = set(grille.positions())

    return [
        (row, column)
        for row in range(grille.size)
        for column in range(grille.size)
        if (row, column) in used
    ]


def _blocks(letters: str, size: int) -> list[str]:
    return [letters[start : start + size] for start in range(0, len(letters), size)]


def encrypt(
    plaintext: str, grille: Grille, direction: Direction = Direction.CLOCKWISE, filler: str = FILLER
) -> str:
    """Fills one grid per block of grille.capacity letters, padding the last."""
    letters = normalize(plaintext)
    letters += filler * (-len(letters) % grille.capacity)
    order = reading_order(grille)
    output: list[str] = []
    for block in _blocks(letters, grille.capacity):
        grid = dict(zip(grille.positions(direction), block, strict=True))
        output.extend(grid[cell] for cell in order)

    return "".join(output)


def decrypt(ciphertext: str, grille: Grille, direction: Direction = Direction.CLOCKWISE) -> str:
    """Inverse transposition; padding letters stay at the end."""
    letters = normalize(ciphertext)
    if len(letters) % grille.capacity:
        raise CiphertextLengthError(
            f"ciphertext length must be a multiple of the grille capacity {grille.capacity}"
        )
    order = reading_order(grille)
    output: list[str] = []
    for block in _blocks(letters, grille.capacity):
        grid = dict(zip(order, block, strict=True))
        output.extend(grid[cell] for cell in grille.positions(direction))

    return "".join(output)
