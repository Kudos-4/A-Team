"""Handles the game state and logic"""

from typing import Optional
import itertools as itools

from checkers.constants.colors import ColorID
from .pieces import Piece, Pawn, King
from .board import Board


class Game:
    def __init__(self, board_size: tuple[int, int]) -> None:
        self._board = Board(board_size)
        self._turn = ColorID.DARK

        self._dark_pieces: list[Piece] = []
        self._light_pieces: list[Piece] = []
        self._populate_board()

    def _populate_board(self) -> None:
        """Add designated pieces to top/bottom three rows' black squares"""
        mapping = {
            ColorID.DARK: self._dark_pieces,
            ColorID.LIGHT: self._light_pieces,
        }
        rows = self._board.rows
        # Assuming rows > 6
        black_rows = ((ColorID.DARK, i) for i in range(3))
        white_rows = ((ColorID.LIGHT, rows - i) for i in range(1, 4))
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
        """Check if can move with respect to tile pieces, turn, and jumps."""
        piece = self._board.piece_at(piece_position)
        
        if piece is None:
            return False
        if piece.color != self._turn:
            return False
        if self._board.piece_at(new_position) is not None:
            return False
        valid_moves = self.get_valid_moves(piece)
        if new_position not in valid_moves:
            return False
        #if jumps are available, only allow jump moves
        all_jumps = self.get_all_jumps(self._turn)
        if all_jumps:
            #check if this move is a jump
            return valid_moves.get(new_position) is not None
        return True

    def move_piece(
        self, piece_position: tuple[int, int], new_position: tuple[int, int]
    ) -> None:
        piece = self._board.piece_at(piece_position)
        valid_moves = self.get_valid_moves(piece)
        
        captured = valid_moves.get(new_position)
        if captured:
            color_list = (self._dark_pieces
                          if captured.color == ColorID.DARK 
                          else self._light_pieces)
            color_list.remove(captured)
            self._board.remove_piece(captured.position)

        self._board.move_piece(piece_position, new_position)
        self._check_promotion(self._board.piece_at(new_position))

        made_capture = any(valid_moves.values())
        can_still_capture = any(self.get_valid_moves(piece).values())
        if made_capture and can_still_capture:
            return
        self.switch_turn()

    def promote_pawn(self, piece: Pawn) -> King:
        """Returns a new King from pawn's attributes if valid"""
        king = King(piece.position, piece.color)
        self._board.update_piece(piece.position, king)
        color_list = (self._dark_pieces
                      if piece.color == ColorID.DARK
                      else self._light_pieces)
        color_list.remove(piece)
        color_list.append(king)
        return king

    def get_valid_moves(
        self, piece: Piece
    ) -> dict[tuple[int, int], Piece] | dict[tuple[int, int], None]:
        """Given a piece, return key-value pairs of possible
        positions and any piece it can take making that move."""
        regular_moves: dict[tuple[int, int], None] = {}
        forced_moves: dict[tuple[int, int], Piece] = {}

        row, col = piece.position
        for dr, dc in piece.moveset:
            destination = (row + dr, col + dc)
            dest_row, dest_col = destination
            if not(0 <= dest_row < self._board.rows and 
                   0 <= dest_col < self._board.cols):
                continue
            target = self._board.piece_at(destination)
            if not target:
                regular_moves[destination] = None
                continue
            # Check for jumps
            if target.color == piece.color:
                continue
            jump = (row + 2 * dr, col + 2 * dc)
            jump_row, jump_col = jump
            if (0 <= jump_row < self._board.rows and
                0 <= jump_col < self._board.cols and
                self._board.piece_at(jump) is None):
                forced_moves[jump] = target
        # Use forced moves if any, else return regular moves
        return forced_moves or regular_moves

    def get_all_jumps(
        self, color: ColorID
    ) -> dict[tuple[int, int], dict[tuple[int, int], Piece]]:
        """Returns all available jump positions for a given color. 
        If one exists, show possible destinations and pieces it'll take"""
        jumps = {}
        pieces = (self._dark_pieces if color == ColorID.DARK
                  else self._light_pieces)
        for piece in pieces:
            moves = self.get_valid_moves(piece)
            piece_jumps = {dest: captured
                           for dest, captured in moves.items()
                           if captured is not None}
            if piece_jumps:
                jumps[piece.position] = piece_jumps
        return jumps
    
    
    def switch_turn(self) -> None:
        #swap whose turn it is after a move
        self._turn = (ColorID.LIGHT
                    if self._turn == ColorID.DARK
                    else ColorID.DARK)
        
    def _check_promotion(self, piece: Piece) -> None:
        #promote pawn if it reached the last row
        if not isinstance(piece, Pawn):
            return
        target_row = self._board.rows - 1 if piece.color == ColorID.DARK else 0
        if piece.position[0] == target_row:
            self.promote_pawn(piece)
    
    def get_game_winner(self) -> Optional[ColorID]:
        """Returns the ColorID of the winner if game is done."""
        mapping = ((ColorID.LIGHT, self.light_pieces), (ColorID.DARK, self.dark_pieces))
        for color, pieces in mapping:
            no_pieces_left = not bool(pieces)
            no_moves_left = not any(map(self.get_valid_moves, pieces))
            if no_pieces_left or no_moves_left:
                return ~color
        return None

    @property
    def turn(self) -> ColorID:
        return self._turn

    @property
    def dark_pieces(self) -> list[Piece]:
        return self._dark_pieces
    
    @property
    def light_pieces(self) -> list[Piece]:
        return self._light_pieces
