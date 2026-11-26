import random

import pytest
from hypothesis import given
from hypothesis import strategies as st

from turning_grille import Direction, Grille, GrilleError, orbit, orbits, rotate

EXAMPLE = Grille.parse(["O...", "....", ".O.O", "..O."])


def test_rotations_are_inverse_quarter_turns() -> None:
    assert rotate((0, 0), 4, Direction.CLOCKWISE) == (0, 3)
    assert rotate((0, 3), 4, Direction.COUNTERCLOCKWISE) == (0, 0)


def test_orbits_partition_the_grid() -> None:
    assert len(orbits(4)) == 4
    assert len(orbits(5)) == 7
    assert orbit((2, 2), 5) == frozenset({(2, 2)})
    assert sum(len(cells) for cells in orbits(9)) == 81


def test_parse_and_print_round_trip() -> None:
    assert str(EXAMPLE) == "O...\n....\n.O.O\n..O."
    assert EXAMPLE.capacity == 16


def test_every_cell_is_exposed_exactly_once() -> None:
    assert sorted(EXAMPLE.positions()) == [(r, c) for r in range(4) for c in range(4)]


def test_odd_center_is_used_once_or_left_out() -> None:
    punched = Grille.from_holes(3, {(0, 0), (0, 1), (1, 1)})
    blank = Grille.from_holes(3, {(0, 0), (0, 1)})

    assert punched.capacity == 9
    assert list(punched.positions()).count((1, 1)) == 1
    assert blank.capacity == 8
    assert blank.center == (1, 1)
    assert EXAMPLE.center is None


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        (["OO", ".."], r"orbit of cell \(0, 0\) has 2 holes"),
        (["..", ".."], "has 0 holes"),
        (["O..", ".."], "square"),
    ],
)
def test_rejects_invalid_drawings(rows: list[str], message: str) -> None:
    with pytest.raises(GrilleError, match=message):
        Grille.parse(rows)


def test_rejects_tiny_sizes_and_holes_outside() -> None:
    with pytest.raises(GrilleError, match="at least 2"):
        Grille.from_holes(1, {(0, 0)})
    with pytest.raises(GrilleError, match=r"hole \(0, 4\) lies outside"):
        Grille.from_holes(4, {(0, 4)})


@given(st.integers(min_value=2, max_value=12), st.integers())
def test_random_grilles_are_valid_and_cover_the_grid(size: int, seed: int) -> None:
    grille = Grille.random(size, random.Random(seed))

    for direction in Direction:
        assert sorted(grille.positions(direction)) == [
            (r, c) for r in range(size) for c in range(size)
        ]
