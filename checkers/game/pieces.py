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
            if new_position == position:
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
        # White is on bottom, therefore it moves up a row diagonally, vice versa.
        if self._color:
            return ((-1, -1), (-1, 1))
        return ((1, -1), (1, 1))


class King(Piece):
    def _get_moveset(self) -> tuple[tuple[int, int], ...]:
        return ((1, -1), (1, 1), (-1, -1), (-1, 1))
