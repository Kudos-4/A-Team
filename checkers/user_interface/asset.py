from PIL import Image, ImageTk
from pathlib import Path

from checkers.colors import ColorID


class AssetHandler:
    directory = Path.cwd() / "checkers" / "user_interface" / "assets"

    LIGHT = ColorID.LIGHT
    DARK = ColorID.DARK

    TILE = "tile"
    PAWN = "pawn"
    KING = "king"

    filepaths = {
        (DARK, TILE): directory / "DarkTile.png",
        (DARK, PAWN): directory / "DarkPawn.png",
        (DARK, KING): directory / "DarkKing.png",
        (LIGHT, TILE): directory / "LightTile.png",
        (LIGHT, PAWN): directory / "LightPawn.png",
        (LIGHT, KING): directory / "LightKing.png",
    }

    def __init__(self, icon_pixel_size: int) -> None:
        self.resolution = (icon_pixel_size, icon_pixel_size)
        self.icons = self._initialize_icons()

    def _initialize_icons(self) -> dict[tuple[ColorID, str], ImageTk.PhotoImage]:
        icons = {}
        for key, path in AssetHandler.filepaths.items():
            image = Image.open(path).resize(self.resolution)
            icons[key] = ImageTk.PhotoImage(image)
        return icons

    def get(self, color: ColorID, type: str) -> ImageTk.PhotoImage:
        key = (color, type)
        return self.icons[key]
