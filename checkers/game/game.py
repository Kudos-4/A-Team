"""Handles the game state and logic"""

from typing import Optional
import itertools as itools

from checkers.colors import ColorID
from checkers.types import Position, Move
from checkers.game import Board, Piece, Pawn, King


class Game:
    def __init__(self, board_size: tuple[int, int]) -> None:
        self._board = Board(board_size)
        self._turn = ColorID.DARK

        self.pieces: dict[ColorID, list[Piece]] = {
            ColorID.DARK: [],
            ColorID.LIGHT: [],
        }
        self._populate_board()

    def _populate_board(self) -> None:
        """
        Initialized pawns to the board following standard Checkers layout.

        Instance pieces dict is modified to store all the pieces.
        This assumes the board size is 8x8.
        """
        rows = self._board.rows
        # Assuming rows > 6
        black_rows = ((ColorID.DARK, i) for i in range(3))
        white_rows = ((ColorID.LIGHT, rows - i) for i in range(1, 4))
        for color_type, row in itools.chain(black_rows, white_rows):
            color_list = self.pieces[color_type]
            start = (row % 2) ^ 1
            for col in range(start, self._board.cols, 2):
                position = (row, col)
                pawn = Pawn(position, color_type)
                self._board.set_piece(position, pawn)
                color_list.append(pawn)

    def can_move_to(self, piece_position: Position, new_position: Position) -> bool:
        """
        Check if a move can be made with respect to tile occupation, turns, and jumps.

        :param piece_position: Piece location
        :type piece_position: Position
        :param new_position: New location for piece to move.
        :type new_position: Position
        :return: If a move is considered legal to perform.
        :rtype: bool
        """
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
        # if jumps are available, only allow jump moves
        if self.get_all_jumps(self._turn):
            # check if this move is a jump
            return valid_moves.get(new_position) is not None
        return True

    def move_piece(self, piece_position: Position, new_position: Position) -> None:
        """
        Moves a piece to the selected position, handles piece promotion,
        and switches turn if no further moves can be made.

        If a promotion is available, pawn is removed and replaced with a king instance.
        This will modify the pieces list and the game's board class.

        :param piece_position: Piece location
        :type piece_position: Position
        :param new_position: Empty target location
        :type new_position: Position
        """
        piece = self._board.piece_at(piece_position)
        assert piece
        valid_moves = self.get_valid_moves(piece)

        if captured := valid_moves.get(new_position):
            color_list = self.pieces[captured.color]
            color_list.remove(captured)
            self._board.remove_piece(captured.position)

        self._board.move_piece(piece_position, new_position)
        self._check_promotion(piece)

        made_capture = any(valid_moves.values())
        can_still_capture = any(self.get_valid_moves(piece).values())
        if made_capture and can_still_capture:
            return
        self._switch_turn()

    def _promote_pawn(self, pawn: Pawn) -> King:
        """
        Returns a new King object from copying Pawn's attributes (except moves).

        This assumes that the promotion is available.

        :param pawn: Pawn being promoted
        :type pawn: Pawn
        :return: New king object
        :rtype: King
        """
        king = King(pawn.position, pawn.color)
        self._board.update_piece(pawn.position, king)
        color_list = self.pieces[pawn.color]
        color_list.remove(pawn)
        color_list.append(king)
        return king

    def get_valid_moves(
        self, piece: Piece
    ) -> dict[Position, Piece] | dict[Position, None]:
        """
        Given a piece, return key-value pairs of possible
        positions and any piece it can take making that move.

        :param piece: Piece on board.
        :type piece: Piece
        :return: All forced moves, or normal moves if no forced moves possible.
        :rtype: dict[Position, Piece] | dict[Position, None]
        """
        regular_moves: dict[Position, None] = {}
        forced_moves: dict[Position, Piece] = {}

        row, col = piece.position
        for dr, dc in piece.moveset:
            destination = (row + dr, col + dc)
            dest_row, dest_col = destination
            if not (
                0 <= dest_row < self._board.rows and 0 <= dest_col < self._board.cols
            ):
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
            if (
                0 <= jump_row < self._board.rows
                and 0 <= jump_col < self._board.cols
                and self._board.piece_at(jump) is None
            ):
                forced_moves[jump] = target
        # Use forced moves if any, else return regular moves
        return forced_moves or regular_moves

    def all_moves_of_color(self, color: ColorID) -> list[Move]:
        """
        Returns all legal moves that can be made for a player's turn.

        :param color: Color of a player
        :type color: ColorID
        :return: List of all possible move pairs.
        :rtype: list[Move]
        """
        all_jumps: list[Move] = []
        all_regular: list[Move] = []

        for piece in self.pieces[color]:
            piece_moves = self.get_valid_moves(piece)
            for destination, captured in piece_moves.items():
                move_list = all_jumps if captured else all_regular
                move = (piece.position, destination)
                move_list.append(move)
        return all_jumps or all_regular

    def get_all_jumps(self, color: ColorID) -> dict[Position, dict[Position, Piece]]:
        """
        Returns all available jump positions for a given color.
        If one exists, show possible destinations and pieces it'll take

        :param color: Color of player
        :type color: ColorID
        :return: Dict of piece position that can make move,
        and the moves that piece can make, along with any captures.
        :rtype: dict[Position, dict[Position, Piece]]
        """
        jumps = {}
        for piece in self.pieces[color]:
            moves = self.get_valid_moves(piece)
            piece_jumps = {
                dest: captured
                for dest, captured in moves.items()
                if captured is not None
            }
            if piece_jumps:
                jumps[piece.position] = piece_jumps
        return jumps

    def _switch_turn(self) -> None:
        # swap whose turn it is after a move
        self._turn = ~self._turn

    def _check_promotion(self, piece: Piece) -> None:
        # promote pawn if it reached the last row
        if not isinstance(piece, Pawn):
            return
        target_row = 0 if piece.color else self._board.rows - 1
        if piece.position[0] == target_row:
            self._promote_pawn(piece)

    def get_game_winner(self) -> Optional[ColorID]:
        """
        Returns the ColorID of the winner if game is done.

        If no winner, return None.

        :return: Color of winner, else None
        :rtype: ColorID | None
        """
        for color, pieces in self.pieces.items():
            no_pieces_left = not pieces
            no_moves_left = not any(map(self.get_valid_moves, pieces))
            if no_pieces_left or no_moves_left:
                return ~color
        return None

    def get_piece_at(self, position: Position) -> Optional[Piece]:
        """
        Piece at a given tile.

        :param position: Target tile
        :type position: Position
        :return: Piece if any
        :rtype: Piece | None
        """
        return self._board[position]

    def get_tile_color_at(self, position: Position) -> ColorID:
        """
        Returns the color of a tile.

        :param position: Target tile
        :type position: Position
        :return: Light tile color or dark tile color.
        :rtype: ColorID
        """
        return self._board.get_color_at(position)

    def get_notation_at(self, position: Position) -> int:
        """
        Gets tile notation or raises ValueError if tile is a light tile.

        :param position: Target tile
        :type position: Position
        :return: Notation value
        :rtype: int
        """
        if notation := self._board.get_notation_at(position):
            return notation
        raise ValueError("Position given does not have a notation.")

    def pieces_of_color(self, color: ColorID) -> list[Piece]:
        """
        Returns a list of all non-captured pieces on the board.

        :param color: Player color
        :type color: ColorID
        :return: Pieces on board.
        :rtype: list[Piece]
        """
        return self.pieces[color]

    @property
    def turn(self) -> ColorID:
        return self._turn

    @property
    def dark_pieces(self) -> list[Piece]:
        return self.pieces[ColorID.DARK]

    @property
    def light_pieces(self) -> list[Piece]:
        return self.pieces[ColorID.LIGHT]
