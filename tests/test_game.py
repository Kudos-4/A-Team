import pytest

from checkers.game.game import Game
from checkers.game.pieces import Piece


@pytest.fixture
def game() -> Game:
    return Game(board_size=(8, 8))


@pytest.fixture
def all_pieces(game: Game) -> list[Piece]:
    return game._black_pieces + game._white_pieces


def test_number_pieces(game: Game) -> None:
    assert len(game._black_pieces) == 12
    assert len(game._white_pieces) == 12


def is_black(position: tuple[int, int]) -> bool:
    return bool(sum(position) % 2)


def test_correct_piece_position(all_pieces: list[Piece]) -> None:
    assert all(is_black(piece.position) for piece in all_pieces)


def test_wrong_piece_position(all_pieces: list[Piece]) -> None:
    all_pieces[0].position = (0, 0)
    assert not all(is_black(piece.position) for piece in all_pieces)
