from abc import ABC, abstractmethod
from typing import Optional

from checkers.user_interface.player import Player
from checkers.game import Game, Position
# This needs to be refactored out
from checkers.game.board import Tile


class GameMode(ABC):
    """Designed to handle inputs/gamestate based on game mode type."""

    def __init__(self, game: Game, players: tuple[Player, Player]) -> None:
        self.player1, self.player2 = players
        self._game: Game = game
        self._selected_tile: Optional[Tile] = None
        # Holds tuple of positions of (old, captured, new)
        self._previous_move: tuple[Position, Optional[Position], Position]
        self._made_valid_move: bool = False

    def get_previous_move(self) -> tuple[Position, Optional[Position], Position]:
        """Return string notation of the previous game move."""
        return self._previous_move

    def get_selected(self) -> Optional[Position]:
        return self._selected_tile.position if self._selected_tile else None

    def get_valid_move_made(self) -> bool:
        return self._made_valid_move

    @abstractmethod
    def tile_pressed(self, position: Position) -> None:
        """Receives a given input to process the state of the game."""
        # Default logic that can be called via super()
        new_tile = self._game._board._tile_at(position)
        self._made_valid_move = self._valid_move_made(position)
        if self._made_valid_move:
            assert self._selected_tile
            self._update_previous_move(self._selected_tile, new_tile)
            self._game.move_piece(self._selected_tile.position, position)
        self._selected_tile = self._updated_selected_tile(new_tile)

    def _valid_move_made(self, position: Position) -> bool:
        """Check if the current piece moved to the selected tile."""
        if not self._selected_tile:
            return False
        if not self._selected_tile.piece:
            return False
        if not self._game.can_move_to(self._selected_tile.position, position):
            return False
        return True

    def _update_previous_move(self, old_tile: Tile, new_tile: Tile) -> None:
        """Update previous move if one is made."""
        if not self._made_valid_move:
            return
        # Selected tile exists and has a piece beyond here
        current_piece = self._game._board[old_tile.position]
        assert current_piece
        all_moves = self._game.get_valid_moves(current_piece)

        # Create string notation
        captured_piece = all_moves.get(new_tile.position)
        captured_position = captured_piece.position if captured_piece else None
        self._previous_move = (old_tile.position, captured_position, new_tile.position)

    def _updated_selected_tile(self, tile: Tile) -> Optional[Tile]:
        """Compute the new selected tile value depending on current state."""
        if self._made_valid_move:
            return None

        piece = tile.piece
        selected_tile = self._selected_tile

        # Only allow selecting own pieces
        if not piece or piece.color != self._game.turn:
            return selected_tile
        # If nothing selected_tile yet, select this tile
        if not selected_tile:
            return tile
        # Clicking same tile deselects it
        if tile is selected_tile:
            return None
        # Clicking another own piece switches selection
        if selected_tile.piece and piece.color == selected_tile.piece.color:
            return tile
        return selected_tile
