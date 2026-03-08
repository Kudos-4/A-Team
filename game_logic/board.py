from typing import Optional
from color_enum import Color
from pieces import Piece


class Tile:
    """Represents a cell on the board"""

    def __init__(self, position: tuple[int, int], color: Color) -> None:
        self._position = position
        self._color = color
        self._notation: Optional[int]
        self._piece: Optional[Piece] = None

    def _calculate_notation(self) -> Optional[int]:
        if self._color == Color.WHITE:
            return None
        rows, columns = self._position
        # 4 black tiles per row
        n_black = rows * 4
        # Count black columns on row depending if even or odd row
        start_index = (rows % 2) ^ 1
        n_black += len(range(start_index, columns + 1, 2))
        return n_black

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @property
    def notation(self) -> Optional[int]:
        if not hasattr(self, "_notation"):
            self._notation = self._calculate_notation()
        return self._notation

    @property
    def color(self) -> Color:
        return self._color

    @property
    def piece(self) -> Optional[Piece]:
        return self._piece

    @piece.setter
    def set_at_tile(self, item: Optional[Piece]) -> None:
        self._piece = item


class Board:
    def __init__(self, board_size: tuple[int, int]) -> None:
        self._board = self._initialize_board(board_size)

    def _initialize_board(
        self, board_size: tuple[int, int]
    ) -> list[list[Tile]]:
        rows, columns = board_size
        # Even rows are just opposite of odd tiles
        odd = [Color(i % 2) for i in range(columns)]
        even = [~color for color in odd]
        board: list[list[Tile]] = []
        for i in range(rows):
            color_map = odd if i % 2 else even
            new_row = [
                Tile(position=(i, j), color=color)
                for j, color in enumerate(color_map)
            ]
            board.append(new_row)
        return board

    def print_notation(self) -> None:
        for row in self._board:
            for tile in row:
                print(f"{tile.notation or '--':02}", end="  ")
            print()

    def print_positions(self) -> None:
        for row in self._board:
            for tile in row:
                print(f"{tile.position}", end="  ")
            print()

    def print_colors(self) -> None:
        for row in self._board:
            for tile in row:
                print(f"{tile.color.value}", end="  ")
            print()


if __name__ == "__main__":
    board = Board((8, 8))
    board.print_notation()
    board.print_positions()
    board.print_colors()
