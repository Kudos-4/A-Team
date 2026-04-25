from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

from checkers.types import Position
from checkers.game import Game

if TYPE_CHECKING:
    from checkers.user_interface import GameScreen


class GameMode(ABC):
    """Designed to handle inputs/gamestate based on game mode type."""

    def __init__(self, game_ui: GameScreen) -> None:
        self._ui = game_ui
        self._game: Game = game_ui.game
        self._selected_tile: Optional[Position] = None
        # Holds tuple of positions of (old, captured, new)
        self._previous_move: tuple[Position, Optional[Position], Position]
        self._made_valid_move: bool = False

    @abstractmethod
    def tile_pressed(self, position: Position) -> None:
        """Processes any user input to the game. Needs to be overridden
        to update the user interface depending on gamemode."""
        self._made_valid_move = self._valid_move_made(position)
        if self._made_valid_move:
            assert self._selected_tile
            self._update_previous_move(self._selected_tile, position)
            self._game.move_piece(self._selected_tile, position)
        self._selected_tile = self._updated_selected_tile(position)

    def _valid_move_made(self, position: Position) -> bool:
        """Check if the current piece moved to the selected tile."""
        if not self._selected_tile:
            return False
        if not self._game.get_piece_at(self._selected_tile):
            return False
        if not self._game.can_move_to(self._selected_tile, position):
            return False
        return True

    def _update_previous_move(self, old: Position, new: Position) -> None:
        """Update previous move if one is made."""
        if not self._made_valid_move:
            return
        # Selected tile exists and has a piece beyond here
        current_piece = self._game._board[old]
        assert current_piece
        all_moves = self._game.get_valid_moves(current_piece)

        # Create string notation
        captured_piece = all_moves.get(new)
        captured_position = captured_piece.position if captured_piece else None
        # captured_position = captured_piece and captured_piece.position
        self._previous_move = (old, captured_position, new)

    def _updated_selected_tile(self, new_position: Position) -> Optional[Position]:
        """Compute the new selected tile value depending on current state."""
        if self._made_valid_move:
            return None

        old_position = self._selected_tile
        piece = self._game.get_piece_at(new_position)

        # Only allow selecting own pieces
        if not piece or piece.color != self._game.turn:
            return old_position
        # If nothing selected_tile yet, select this tile
        if not old_position:
            return new_position
        # Clicking same tile deselects it
        if new_position == old_position:
            return None
        # Clicking another own piece switches selection
        current_piece = self._game.get_piece_at(old_position)
        if current_piece and piece.color == current_piece.color:
            return new_position
        return old_position

    def get_previous_move(self) -> tuple[Position, Optional[Position], Position]:
        """Return string notation of the previous game move."""
        return self._previous_move

    def get_selected(self) -> Optional[Position]:
        return self._selected_tile

    def get_valid_move_made(self) -> bool:
        return self._made_valid_move
