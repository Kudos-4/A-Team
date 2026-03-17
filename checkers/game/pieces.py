from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import final

from checkers.constants.colors import ColorID


@dataclass
class Piece(ABC):
    """
    Holds only the data for the piece. Pieces should not have any methods
    relating to checkers. Only to update their data.
    """

    _position: tuple[int, int]
    _color: ColorID
    _moveset: tuple[tuple[int, int], ...] = field(init=False)

    def __post_init__(self):
        self._moveset = self._get_moveset()

    @abstractmethod
    def _get_moveset(self) -> tuple[tuple[int, int], ...]:
        pass

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, new_position: tuple[int, int]) -> None:
        self._position = new_position

    @property
    def color(self) -> ColorID:
        return self._color

    @property
    def moveset(self) -> tuple[tuple[int, int], ...]:
        return self._moveset
    
    @final
    def __bool__(self):
        return True


class Pawn(Piece):
    def _get_moveset(self) -> tuple[tuple[int, int], ...]:
        # White is on bottom, therefore it moves up a row diagonally, vice versa.
        if self._color:
            return ((-1, -1), (-1, 1))
        return ((1, -1), (1, 1))


class King(Piece):
    def _get_moveset(self) -> tuple[tuple[int, int], ...]:
        return ((1, -1), (1, 1), (-1, -1), (-1, 1))
