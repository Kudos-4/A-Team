"""Handles the game state and logic"""

import itertools as itools

from checkers.constants.colors import ColorID
from .pieces import Piece, Pawn, King
from .board import Board


class Game:
    def __init__(self, board_size: tuple[int, int]) -> None:
        self._board = Board(board_size)
        self._turn = ColorID.BLACK

        self._black_pieces: list[Piece] = []
        self._white_pieces: list[Piece] = []
        self._populate_board()

    def _populate_board(self) -> None:
        """Add designated pieces to top/bottom three rows' black squares"""
        mapping = {
            ColorID.BLACK: self._black_pieces,
            ColorID.WHITE: self._white_pieces,
        }
        rows = self._board.rows
        # Assuming rows > 6
        black_rows = ((ColorID.BLACK, i) for i in range(3))
        white_rows = ((ColorID.WHITE, rows - i) for i in range(1, 4))
        for color_type, row in itools.chain(black_rows, white_rows):
            color_list = mapping[color_type]
            start = (row % 2) ^ 1
            for col in range(start, self._board.cols, 2):
                position = (row, col)
                pawn = Pawn(position, color_type)
                self._board.set_piece(position, pawn)
                color_list.append(pawn)

    def can_move_to(
        self, piece_position: tuple[int, int], new_position: tuple[int, int]
    ) -> bool:
        """
        Checks if piece can move, if piece can move to spot based on
        position and tile's vacancy.
        """
        raise NotImplementedError()

    def move_piece(
        self, piece_position: tuple[int, int], new_position: tuple[int, int]
    ) -> None:
        # can_move_to() should be checked first
        # Also needs to check if is capturing

        # For now, just move piece
        self._board.move_piece(piece_position, new_position)

    def promote_pawn(self, piece: Pawn) -> King:
        """Returns a new King from pawn's attributes if valid"""
        # Return King object, replace pawn in list and on board
        if not isinstance(piece, Pawn):
            raise ValueError(
                f"Pawn can only be promoted, but received {type(piece)}"
            )
        raise NotImplementedError()
