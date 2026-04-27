from PIL import Image, ImageTk
from pathlib import Path

from checkers.colors import ColorID

ICON_DIRECTORY = Path.cwd() / "checkers" / "user_interface" / "assets"


class AssetHandler:
    """
    Holds access to icons of the checker board.

    Accessing images requires both a color
    and an item type.

    :var LIGHT: Color of the icon type
    :vartype LIGHT: Literal[ColorID.LIGHT]
    :var DARK: Color of the icon type
    :vartype DARK: Literal[ColorID.DARK]
    :var TILE: Item type for image access
    :vartype TILE: Literal['tile']
    :var PAWN: Item type for image access
    :vartype PAWN: Literal['pawn']
    :var KING: Item type for image access
    :vartype KING: Literal['king']
    :var filepaths: Description
    :vartype filepaths: dict[tuple[ColorID, str], Path]
    """

    LIGHT = ColorID.LIGHT
    DARK = ColorID.DARK

    TILE = "tile"
    PAWN = "pawn"
    KING = "king"

    filepaths = {
        (DARK, TILE): ICON_DIRECTORY / "DarkTile.png",
        (DARK, PAWN): ICON_DIRECTORY / "DarkPawn.png",
        (DARK, KING): ICON_DIRECTORY / "DarkKing.png",
        (LIGHT, TILE): ICON_DIRECTORY / "LightTile.png",
        (LIGHT, PAWN): ICON_DIRECTORY / "LightPawn.png",
        (LIGHT, KING): ICON_DIRECTORY / "LightKing.png",
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
        """
        Return the icon given the color and image type constant.

        :param color: Color of selected piece or tile
        :type color: ColorID
        :param type: String literal of the item type (tile, pawn, king)
        :type type: str
        :return: Description
        :rtype: PhotoImage
        """
        key = (color, type)
        return self.icons[key]
