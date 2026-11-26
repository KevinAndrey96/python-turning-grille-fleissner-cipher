import io
import subprocess
import sys

import pytest

from turning_grille import Grille
from turning_grille.cli import main

EXAMPLE = "O.../..../.O.O/..O."


def run(argv: list[str], stdin: str = "") -> tuple[int, str]:
    output = io.StringIO()
    status = main(argv, stdin=io.StringIO(stdin), stdout=output)

    return status, output.getvalue()


def test_encrypts_and_decrypts() -> None:
    assert run(["encrypt", "-g", EXAMPLE, "-d", "ccw", "Jim attacks at dawn"]) == (
        0,
        "JKTDSAATWIAMCNAT\n",
    )
    assert run(["decrypt", "-g", EXAMPLE, "-d", "ccw"], "JKTD SAAT WIAM CNAT") == (
        0,
        "JIMATTACKSATDAWN\n",
    )


def test_generates_reproducible_valid_grilles() -> None:
    status, output = run(["generate", "-n", "6", "--seed", "7"])

    assert status == 0
    assert output == run(["generate", "-n", "6", "--seed", "7"])[1]
    assert Grille.parse(output.strip().split("/")).size == 6


def test_generates_without_a_seed() -> None:
    status, output = run(["generate", "-n", "4"])

    assert status == 0
    assert Grille.parse(output.strip().split("/")).size == 4


def test_search_lists_candidates() -> None:
    status, output = run(["search", "-n", "4", "-c", "attacks", "JKTDSAATWIAMCNAT"])

    assert status == 0
    assert output.splitlines()[0] == "O.../..../.O.O/..O. counterclockwise: JIMATTACKSATDAWN"


@pytest.mark.parametrize(
    "argv",
    [
        ["encrypt", "-g", "OO/..", "hola"],
        ["decrypt", "-g", EXAMPLE, "ABC"],
        ["search", "-n", "8", "-c", "x", "ABC"],
    ],
)
def test_reports_errors_with_exit_code_two(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(argv) == (2, "")
    assert capsys.readouterr().err.startswith("error:")


def test_module_entry_point() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "turning_grille", "encrypt", "-g", EXAMPLE, "-d", "ccw", "jim"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert completed.stdout == "JXXXXXXXXIXMXXXX\n"
