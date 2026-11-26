"""Exhaustive search over every valid grille of a small size.

An n x n grille picks one cell in each of floor(n^2 / 4) orbits, so there
are 4^floor(n^2 / 4) grilles (twice that on odd sizes, center punched or
not) and two turning directions: 512 candidates for 4 x 4, about half a
million for 6 x 6 and about 2.3 x 10^15 for 10 x 10.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from itertools import product

from turning_grille.cipher import decrypt, normalize
from turning_grille.grille import Direction, Grille, orbits

MAX_SEARCH_SIZE = 6


class SearchSpaceError(ValueError):
    """Raised when exhaustive search is not feasible or not meaningful."""


@dataclass(frozen=True, slots=True)
class Candidate:
    grille: Grille
    direction: Direction
    plaintext: str


def all_grilles(size: int) -> Iterator[Grille]:
    if not 2 <= size <= MAX_SEARCH_SIZE:
        raise SearchSpaceError(f"exhaustive search supports sizes 2 to {MAX_SEARCH_SIZE}")
    groups = orbits(size)
    rotating = [sorted(cells) for cells in groups if len(cells) == 4]
    centers: list[tuple[tuple[int, int], ...]] = [()]
    centers += [tuple(cells) for cells in groups if len(cells) == 1]
    for center in centers:
        for holes in product(*rotating):
            yield Grille.from_holes(size, (*holes, *center))


def search(ciphertext: str, size: int, crib: str) -> list[Candidate]:
    """Every grille and direction whose decryption contains the crib."""
    expected = normalize(crib)
    if not expected:
        raise SearchSpaceError("crib must contain at least one letter")
    letters = normalize(ciphertext)
    matches: list[Candidate] = []
    for grille in all_grilles(size):
        if len(letters) < grille.capacity:
            continue
        block = letters[: grille.capacity]
        for direction in Direction:
            plaintext = decrypt(block, grille, direction)
            if expected in plaintext:
                matches.append(Candidate(grille, direction, plaintext))

    return matches
