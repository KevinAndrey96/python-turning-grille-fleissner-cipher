import pytest

from turning_grille import Direction, Grille, SearchSpaceError, all_grilles, encrypt, search


def test_counts_every_grille() -> None:
    assert sum(1 for _ in all_grilles(4)) == 256
    assert sum(1 for _ in all_grilles(3)) == 32


def test_finds_the_original_grille_and_its_rotation() -> None:
    found = search("JKTDSAATWIAMCNAT", 4, "attacks")

    assert [(str(item.grille), item.direction, item.plaintext) for item in found] == [
        ("O...\n....\n.O.O\n..O.", Direction.COUNTERCLOCKWISE, "JIMATTACKSATDAWN"),
        ("...O\n.O..\nO...\n.O..", Direction.COUNTERCLOCKWISE, "DAWNJIMATTACKSAT"),
    ]


def test_finds_odd_grilles() -> None:
    grille = Grille.from_holes(5, {(0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (2, 2)})
    ciphertext = encrypt("The enemy moves at night", grille)

    assert any(item.grille == grille for item in search(ciphertext, 5, "enemymoves"))


def test_skips_grilles_larger_than_the_text() -> None:
    assert search("ABCDEFGH", 3, "ABC") != []
    assert search("ABC", 4, "ABC") == []


@pytest.mark.parametrize(("size", "crib"), [(7, "ABC"), (1, "ABC"), (4, "123")])
def test_rejects_unfeasible_searches(size: int, crib: str) -> None:
    with pytest.raises(SearchSpaceError):
        search("ABCDEFGHIJKLMNOP", size, crib)
