from typing import Optional

from checkers.colors import ColorID
from checkers.game import Piece
from checkers.types import Position


class Tile:
    """Represents a cell on the board. Tiles should only be accessed through Board."""

    def __init__(self, position: Position, color: ColorID) -> None:
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
        rows, col = self._position
        previous_rows = rows * 4  # 4 black tiles per row
        # Doesn't matter if row is odd/even with int division
        current_row = (col // 2) + 1
        return previous_rows + current_row

    @property
    def position(self) -> Position:
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
    """
    Handles the state of the checkers game.
    Any validations such as moves, promotions, and game status
    belong in the Game class.
    """

    def __init__(self, board_size: tuple[int, int]) -> None:
        self._rows, self._cols = self.size = board_size
        self._board = self._initialize_board()

    def _initialize_board(self) -> list[list[Tile]]:
        odd = [ColorID(i % 2) for i in range(self._cols)]
        # Even rows are opposite of odd tiles; use negate
        even = [~color for color in odd]
        board: list[list[Tile]] = []
        for i in range(self._rows):
            color_list = odd if i % 2 else even
            new_row = [
                Tile(position=(i, j), color=color) for j, color in enumerate(color_list)
            ]
            board.append(new_row)
        return board

    def set_piece(self, position: Position, piece: Piece) -> None:
        """Add piece to an empty spot."""
        tile = self._tile_at(position)
        if tile.piece:
            raise ValueError("Position is already occupied with piece.")
        tile.piece = piece

    def move_piece(self, position: Position, new_position: Position) -> None:
        """Move piece to an empty space. Does not handle if piece can reach; game controls rules."""
        # Board should modify tile.piece and update Piece.position
        current_tile = self._tile_at(position)
        new_tile = self._tile_at(new_position)
        if not current_tile.piece or new_tile.piece:
            raise ValueError(
                "Current tile is empty or piece already occupies target location."
            )
        new_tile.piece = current_tile.piece
        current_tile.piece = None
        new_tile.piece.position = new_position

    def update_piece(self, position: Position, new_piece: Piece) -> None:
        tile = self._tile_at(position)
        if tile.piece is None:
            raise ValueError("No piece at position to replace.")
        tile.piece = new_piece

    def remove_piece(self, position: Position) -> None:
        tile = self._tile_at(position)
        if tile.piece is None:
            raise ValueError("No piece at position to be removed")
        tile.piece = None

    def _tile_at(self, position: Position) -> Tile:
        row, col = position
        return self._board[row][col]

    def piece_at(self, position: Position) -> Optional[Piece]:
        return self._tile_at(position).piece

    def __getitem__(self, position: Position) -> Optional[Piece]:
        """Same as piece_at()"""
        return self.piece_at(position)

    def get_color_at(self, position: Position) -> ColorID:
        return self._tile_at(position).color

    def get_notation_at(self, position: Position) -> Optional[int]:
        return self._tile_at(position).notation

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

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
