from checkers.game.pieces import Pawn, King
from checkers.constants.colors import ColorID


def test_king_not_pawn() -> None:
    king = King((0, 0), ColorID.BLACK)
    assert not isinstance(king, Pawn)
