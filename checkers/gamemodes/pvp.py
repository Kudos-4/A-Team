from checkers.types import Position
from checkers.gamemodes import GameMode


class PvPGameMode(GameMode):
    """Essentially the same as GameMode class.
    Accepts any inputs for either light or dark user."""

    def tile_pressed(self, position: Position) -> None:
        super().tile_pressed(position)
        self._ui.update_interface()
