import pytest

from checkers.game import Game, Piece


@pytest.fixture
def game() -> Game:
    return Game(board_size=(8, 8))


@pytest.fixture
def all_pieces(game: Game) -> list[Piece]:
    return game.dark_pieces + game.light_pieces


def test_number_pieces(game: Game) -> None:
    assert len(game.dark_pieces) == 12
    assert len(game.light_pieces) == 12


def is_black(position: tuple[int, int]) -> bool:
    return bool(sum(position) % 2)


def test_correct_piece_position(all_pieces: list[Piece]) -> None:
    assert all(is_black(piece.position) for piece in all_pieces)


def test_wrong_piece_position(all_pieces: list[Piece]) -> None:
    all_pieces[0].position = (0, 0)
    assert not all(is_black(piece.position) for piece in all_pieces)
