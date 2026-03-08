from checkers.game.pieces import Pawn, King
from checkers.game.color_enum import Color


def test_king_not_pawn() -> None:
    king = King((0, 0), Color.BLACK)
    assert not isinstance(king, Pawn)
