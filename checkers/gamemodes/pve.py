from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import random
import copy

from checkers.user_interface import Player
from checkers.types import Position, Move
from checkers.game import Piece, King
from checkers.gamemodes import GameMode

if TYPE_CHECKING:
    from checkers.user_interface import GameScreen


class GameState(GameMode):
    """Isolated game copy to emulate player-computer interactions."""

    def __init__(self, game_ui: GameScreen) -> None:
        super().__init__(game_ui)
        del self._ui

    def tile_pressed(self, position: Position) -> None:
        return super().tile_pressed(position)


class PvEGameMode(GameMode):
    def __init__(self, game_ui: GameScreen, players: tuple[Player, Player]) -> None:
        super().__init__(game_ui)
        self._player1, self._player2 = players
        self.max_depth: int = 2
        self.move_delay_ms: int = 500
        self._gamestate = GameState(game_ui)
        if self.is_computers_turn():
            self._make_move()

    def tile_pressed(self, position: Position) -> None:
        """Ignores any user tile clicks while computer is making move."""
        if self.is_computers_turn():
            return

        # Player interaction
        super().tile_pressed(position)
        self._ui.update_interface()

        # Make computer move afterwards
        if self._game.get_game_winner() is not None:
            return
        # In case of player's multiple captures
        if not self.is_computers_turn():
            return
        self._make_move()

    def is_computers_turn(self) -> bool:
        return self._player2.color == self._game.turn

    def _make_move(self) -> None:
        best_moves = self._compute_best_moves()
        if not best_moves:
            raise Exception("Computer cannot find a move from MiniMax algorithm.")
        random_i = random.randint(0, len(best_moves) - 1)
        first, second = best_moves[random_i]
        self._ui.after(self.move_delay_ms, lambda: self._press_tile(first))
        self._ui.after(2 * self.move_delay_ms, lambda: self._press_tile(second))
        self._ui.after(3 * self.move_delay_ms, self._check_forced_move)

    def _press_tile(self, position: Position) -> None:
        super().tile_pressed(position)
        self._gamestate.tile_pressed(position)
        self._ui.update_interface()

    def _check_forced_move(self) -> None:
        if self.is_computers_turn():
            self._make_move()

    def _compute_best_moves(self) -> list[Move]:
        """Iterates through all moves and returns the best moves that can be made."""
        highest_score: Optional[int] = None
        best_moves: list[Move] = []

        for move in self._game.all_moves_of_color(self._game.turn):
            gamestate = self._new_gamestate(self._gamestate, move)
            score = self._minimax(gamestate, self.max_depth)
            if highest_score is None:
                highest_score = score
                best_moves.append(move)
            elif score == highest_score:
                best_moves.append(move)
            elif score > highest_score:
                highest_score = score
                best_moves.clear()
                best_moves.append(move)
        return best_moves

    def _minimax(self, gamestate: GameState, depth: int) -> int:
        """Recursively searches all decision with a given depth
        using score function to evaluate the best move."""
        if not depth or gamestate._game.get_game_winner() is not None:
            return self._score_by_piece_value(gamestate)

        # Maximize score for computer, minimize score for human
        # This makes it assume the player plays optimally
        # Getting the best move from biggest difference in score
        maximize_score = self._player2.color == gamestate._game.turn
        best: Optional[int] = None
        comparator = max if maximize_score else min

        for move in gamestate._game.all_moves_of_color(gamestate._game.turn):
            new_gamestate = self._new_gamestate(gamestate, move)
            score = self._minimax(new_gamestate, depth - 1)
            best = score if best is None else comparator(best, score)
        assert best is not None
        return best

    def _score_by_piece_value(self, gamestate: GameState) -> int:
        """Evaluate by piece count with a king as additional value."""
        player_pieces = gamestate._game.pieces_of_color(self._player1.color)
        player_value = len(player_pieces) + self._number_of_kings(player_pieces)

        computer_pieces = gamestate._game.pieces_of_color(self._player2.color)
        computer_value = len(computer_pieces) + self._number_of_kings(computer_pieces)
        return computer_value - player_value

    def _number_of_kings(self, pieces: list[Piece]):
        return sum(isinstance(piece, King) for piece in pieces)

    def _new_gamestate(self, gamestate: GameState, move: Move) -> GameState:
        """Create new gamestate from the move decision."""
        gamestate = copy.deepcopy(self._gamestate)
        for position in move:
            gamestate.tile_pressed(position)
        return gamestate
