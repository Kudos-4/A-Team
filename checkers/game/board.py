from typing import Optional
from checkers.constants.colors import ColorID
from .pieces import Piece


class Tile:
    """Represents a cell on the board. Tiles should only be accessed through Board"""

    def __init__(self, position: tuple[int, int], color: ColorID) -> None:
        self._position = position
        self._color = color
        self._notation: Optional[int]
        self._piece: Optional[Piece] = None

    def _calculate_notation(self) -> Optional[int]:
        """
        Return a tile's notation (black square) by counting
        how many black squares from top to current row.
        """
        if self._color:
            return None
        rows, cols = self._position
        n_black = rows * 4  # 4 black tiles per row
        # Count how many black tiles on current row
        # If odd row, count black squares starting at 0, else 1
        start_index = (rows % 2) ^ 1
        n_black += len(range(start_index, cols + 1, 2))
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
    def color(self) -> ColorID:
        return self._color

    @property
    def piece(self) -> Optional[Piece]:
        return self._piece

    @piece.setter
    def piece(self, item: Optional[Piece]) -> None:
        self._piece = item


class Board:
    def __init__(self, board_size: tuple[int, int]) -> None:
        self.rows, self.cols = self.size = board_size
        self._board = self._initialize_board()

    def _initialize_board(self) -> list[list[Tile]]:
        odd = [ColorID(i % 2) for i in range(self.cols)]
        # Even rows are opposite of odd tiles; use negate
        even = [~color for color in odd]
        board: list[list[Tile]] = []
        for i in range(self.rows):
            color_list = odd if i % 2 else even
            new_row = [
                Tile(position=(i, j), color=color)
                for j, color in enumerate(color_list)
            ]
            board.append(new_row)
        return board

    def __getitem__(self, key: int) -> list[Tile]:
        """To index by rows and columns."""
        return self._board[key]

    def piece_at(self, position: tuple[int, int]) -> Optional[Piece]:
        row, col = position
        tile = self._board[row][col]
        return tile.piece

    def get_black_tiles_at(self, row: int) -> tuple[Tile, ...]:
        """Return only the black tiles at a specified row."""
        current_row = self._board[row]
        _, cols = self.size
        start = (row % 2) ^ 1
        black_indices = range(start, cols, 2)
        return tuple(current_row[i] for i in black_indices)

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

    def print_tile_colors(self) -> None:
        for row in self._board:
            for tile in row:
                print(f"{tile.color.value}", end="  ")
            print()

    def print_pieces(self) -> None:
        for row in self._board:
            for tile in row:
                if tile.piece is None:
                    tile_type = "_"
                else:
                    tile_type = tile.piece.color.value
                print(f"{tile_type}", end="  ")
            print()


if __name__ == "__main__":
    board = Board((8, 8))
    board.get_black_tiles_at(1)
