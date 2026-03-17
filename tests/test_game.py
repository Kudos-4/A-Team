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


def is_black(cols: int, position: tuple[int, int]) -> bool:
    row, col = position
    start = (row % 2) ^ 1
    return col in range(start, cols, 2)


def test_correct_piece_position(game: Game, all_pieces: list[Piece]) -> None:
    assert all(
        is_black(game._board.cols, piece.position) for piece in all_pieces
    )


def test_wrong_piece_position(game: Game) -> None:
    all_pieces = game._black_pieces + game._white_pieces
    all_pieces[0].position = (0, 0)
    assert not all(
        is_black(game._board.cols, piece.position) for piece in all_pieces
    )
