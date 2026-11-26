import random

import pytest
from hypothesis import given
from hypothesis import strategies as st

from turning_grille import CiphertextLengthError, Direction, Grille, decrypt, encrypt, normalize

EXAMPLE = Grille.parse(["O...", "....", ".O.O", "..O."])
NINE = Grille.from_holes(
    9,
    [
        (0, 0), (0, 3), (0, 5), (1, 2), (1, 8), (2, 1), (2, 6), (3, 2), (3, 4), (3, 7), (4, 4),
        (4, 6), (4, 8), (5, 3), (5, 7), (6, 0), (6, 5), (7, 1), (7, 4), (7, 8), (8, 2),
    ],
)  # fmt: skip
NINE_PLAINTEXT = (
    "THIS IS A MESSAGE THAT I AM ENCRYPTING WITH A TURNING GRILLE "
    "TO PROVIDE THIS ILLUSTRATIVE EXAMPLE"
)
NINE_CIPHERTEXT = (
    "TESHN INCIG LSRGY LRIUS PITSA TLILM REENS ATTOG SIAWG IPVER TOTEH HVAEA XITDT UAIME "
    "RANPM TLHIE I"
)


def test_reproduces_the_original_four_by_four_example() -> None:
    ciphertext = encrypt("Jim attacks at dawn", EXAMPLE, Direction.COUNTERCLOCKWISE)

    assert ciphertext == "JKTDSAATWIAMCNAT"
    assert decrypt("JKTD SAAT WIAM CNAT", EXAMPLE, Direction.COUNTERCLOCKWISE) == (
        "JIMATTACKSATDAWN"
    )


def test_reproduces_the_original_nine_by_nine_example() -> None:
    assert decrypt(NINE_CIPHERTEXT, NINE, Direction.COUNTERCLOCKWISE) == normalize(NINE_PLAINTEXT)
    assert encrypt(NINE_PLAINTEXT, NINE, Direction.COUNTERCLOCKWISE) == normalize(NINE_CIPHERTEXT)


def test_long_texts_use_several_grids_and_padding() -> None:
    ciphertext = encrypt("A" * 20, EXAMPLE)

    assert len(ciphertext) == 32
    assert decrypt(ciphertext, EXAMPLE) == "A" * 20 + "X" * 12


def test_odd_grille_without_center_skips_that_cell() -> None:
    grille = Grille.from_holes(3, {(0, 0), (0, 1)})
    ciphertext = encrypt("ABCDEFGH", grille)

    assert len(ciphertext) == 8
    assert decrypt(ciphertext, grille) == "ABCDEFGH"


def test_rejects_partial_grids() -> None:
    with pytest.raises(CiphertextLengthError, match="multiple of the grille capacity 16"):
        decrypt("ABC", EXAMPLE)


@given(
    st.text(),
    st.integers(min_value=2, max_value=8),
    st.integers(),
    st.sampled_from(list(Direction)),
)
def test_decrypt_inverts_encrypt(text: str, size: int, seed: int, direction: Direction) -> None:
    grille = Grille.random(size, random.Random(seed))
    letters = normalize(text)
    recovered = decrypt(encrypt(text, grille, direction), grille, direction)

    assert recovered.startswith(letters)
    assert set(recovered[len(letters) :]) <= {"X"}
