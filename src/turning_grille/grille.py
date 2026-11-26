"""Fleissner turning grille: a square card with holes that, over four quarter
turns, exposes every cell of the grid exactly once."""

from __future__ import annotations

import random
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import StrEnum

type Cell = tuple[int, int]

HOLE = "O"
SOLID = "."


class Direction(StrEnum):
    CLOCKWISE = "clockwise"
    COUNTERCLOCKWISE = "counterclockwise"


class GrilleError(ValueError):
    """Raised when a grille does not cover every cell exactly once."""


def rotate(cell: Cell, size: int, direction: Direction) -> Cell:
    """Where a hole moves after a quarter turn of the card."""
    row, column = cell
    if direction is Direction.CLOCKWISE:
        return column, size - 1 - row

    return size - 1 - column, row


def orbit(cell: Cell, size: int) -> frozenset[Cell]:
    """The cells a hole visits over four quarter turns."""
    cells = {cell}
    current = cell
    for _ in range(3):
        current = rotate(current, size, Direction.CLOCKWISE)
        cells.add(current)

    return frozenset(cells)


def orbits(size: int) -> list[frozenset[Cell]]:
    """Partition of the grid into rotation orbits, in reading order."""
    seen: set[Cell] = set()
    result: list[frozenset[Cell]] = []
    for row in range(size):
        for column in range(size):
            if (row, column) not in seen:
                current = orbit((row, column), size)
                seen |= current
                result.append(current)

    return result


@dataclass(frozen=True, slots=True)
class Grille:
    """A valid grille has exactly one hole in each four-cell orbit.

    On odd sizes the center cell is its own orbit; when it is punched it is
    used only in the first position, otherwise it is left as filler.
    """

    size: int
    holes: frozenset[Cell]

    def __post_init__(self) -> None:
        if self.size < 2:
            raise GrilleError("grille size must be at least 2")
        outside = [cell for cell in self.holes if not all(0 <= x < self.size for x in cell)]
        if outside:
            raise GrilleError(f"hole {min(outside)} lies outside a {self.size} x {self.size} grid")
        for cells in orbits(self.size):
            punched = len(cells & self.holes)
            if len(cells) == 4 and punched != 1:
                first = min(cells)
                raise GrilleError(
                    f"the rotation orbit of cell {first} has {punched} holes, it needs exactly 1"
                )

    @classmethod
    def from_holes(cls, size: int, holes: Iterable[Cell]) -> Grille:
        return cls(size, frozenset(holes))

    @classmethod
    def parse(cls, rows: Iterable[str]) -> Grille:
        """Reads a drawing where O marks a hole and any other character is solid."""
        lines = [line.strip() for line in rows if line.strip()]
        if any(len(line) != len(lines) for line in lines):
            raise GrilleError("grille drawing must be square")
        holes = {
            (row, column)
            for row, line in enumerate(lines)
            for column, char in enumerate(line)
            if char.upper() == HOLE
        }

        return cls(len(lines), frozenset(holes))

    @classmethod
    def random(cls, size: int, rng: random.Random) -> Grille:
        """Picks one hole per orbit; odd sizes always punch the center."""
        holes = [rng.choice(sorted(cells)) for cells in orbits(size)]

        return cls(size, frozenset(holes))

    @property
    def center(self) -> Cell | None:
        return (self.size // 2, self.size // 2) if self.size % 2 else None

    @property
    def capacity(self) -> int:
        """Letters per block: every cell, minus an unpunched odd center."""
        unused = self.center is not None and self.center not in self.holes

        return self.size * self.size - int(unused)

    def positions(self, direction: Direction = Direction.CLOCKWISE) -> Iterator[Cell]:
        """Cells in writing order: holes in reading order, then turn the card."""
        holes = set(self.holes)
        for turn in range(4):
            for cell in sorted(holes):
                if turn == 0 or cell != self.center:
                    yield cell
            holes = {rotate(cell, self.size, direction) for cell in holes}

    def __str__(self) -> str:
        return "\n".join(
            "".join(HOLE if (row, column) in self.holes else SOLID for column in range(self.size))
            for row in range(self.size)
        )
