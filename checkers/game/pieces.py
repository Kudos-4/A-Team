from abc import ABC, abstractmethod
from checkers.constants.colors import ColorID


class Piece(ABC):
    def __init__(self, position: tuple[int, int], color: ColorID) -> None:
        self._position = position
        self._color = color
        self._moveset = self._get_moveset()

    @abstractmethod
    def _get_moveset(self) -> tuple[tuple[int, int], ...]:
        pass

    def can_move_to(self, position: tuple[int, int]) -> bool:
        for move in self._moveset:
            new_position = tuple(map(sum, zip(self._position, move)))
            if position == new_position:
                return True
        return False

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @property
    def color(self) -> ColorID:
        return self._color

    @property
    def moveset(self) -> tuple[tuple[int, int], ...]:
        return self._moveset


class Pawn(Piece):
    def _get_moveset(self) -> tuple[tuple[int, int], ...]:
        # Black is on top, therefore it moves down a row diagonally
        if self._color == ColorID.BLACK:
            return ((1, -1), (1, 1))
        return ((-1, -1), (-1, 1))


class King(Piece):
    def _get_moveset(self) -> tuple[tuple[int, int], ...]:
        return ((1, -1), (1, 1), (-1, -1), (-1, 1))


if __name__ == "__main__":
    piece = Pawn((0, 1), ColorID.BLACK)
    print(piece.color)
