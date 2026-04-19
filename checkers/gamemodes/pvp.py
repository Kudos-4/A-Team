from .gamemode import GameMode


class PvPGameMode(GameMode):
    """Essentially the same as GameMode class.
    Accepts any inputs for either light or dark user."""
    def tile_pressed(self, position: tuple[int, int]) -> None:
        return super().tile_pressed(position)
