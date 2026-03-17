import pytest

from checkers.game.pieces import Pawn, King
from checkers.constants.colors import ColorID


@pytest.fixture
def white_pawn() -> Pawn:
    return Pawn(_position=(0, 0), _color=ColorID.WHITE)


@pytest.fixture
def black_pawn() -> Pawn:
    return Pawn(_position=(0, 4), _color=ColorID.BLACK)


@pytest.fixture
def white_king() -> King:
    return King(_position=(1, 2), _color=ColorID.WHITE)


@pytest.fixture
def black_king() -> King:
    return King(_position=(1, 2), _color=ColorID.BLACK)


def test_king_not_pawn() -> None:
    king = King((0, 0), ColorID.BLACK)
    assert not isinstance(king, Pawn)


def test_white_pawn_moveset(white_pawn: Pawn, black_pawn: King) -> None:
    assert white_pawn.moveset == ((-1, -1), (-1, 1))
    assert black_pawn.moveset == ((1, -1), (1, 1))


def test_king_moveset(white_king: King, black_king: King) -> None:
    oracle = ((1, -1), (1, 1), (-1, -1), (-1, 1))
    assert white_king.moveset == oracle
    assert black_king.moveset == oracle


def test_raise_on_set_color(white_pawn: Pawn, black_king: King) -> None:
    with pytest.raises(AttributeError):
        white_pawn.color = ColorID.BLACK
    with pytest.raises(AttributeError):
        black_king.color = ColorID.WHITE


def test_raise_on_set_moves(black_pawn: Pawn, white_king: King) -> None:
    with pytest.raises(AttributeError):
        black_pawn.moveset = ((1, -1), (1, 1))
    with pytest.raises(AttributeError):
        white_king.moveset = ((1, -1), (1, 1))
