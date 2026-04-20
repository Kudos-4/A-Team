from checkers.game import Position
from checkers.gamemodes import GameMode


class PvEGameMode(GameMode):
    def tile_pressed(self, position: Position) -> None:
        """Ignores any user tile clicks while computer is making move."""
        if not self._is_users_turn():
            return
        super().tile_pressed(position)
        move = self._compute_next_move()
        self._execute_moves(move)

    def _is_users_turn(self) -> bool:
        return self.player1.color == self._game.turn

    def _compute_next_move(self) -> tuple[Position, Position]:
        """Choose a possible move and return the piece and target position"""
        raise NotImplementedError()

    def _execute_moves(self, moves: tuple[Position, Position]) -> None:
        raise NotImplementedError()
        for position in moves:
            # I don't know if this actually works or not
            super().tile_pressed(position)
