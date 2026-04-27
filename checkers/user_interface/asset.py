from PIL import Image, ImageTk
from pathlib import Path

from checkers.colors import ColorID

ICON_DIRECTORY = Path.cwd() / "checkers" / "user_interface" / "assets"


class AssetHandler:
    """
    Holds access to icons of the checker board.

    Accessing images requires both a color
    and an item type.

    :var TILE: Item type for image access
    :vartype TILE: Literal['tile']
    :var PAWN: Item type for image access
    :vartype PAWN: Literal['pawn']
    :var KING: Item type for image access
    :vartype KING: Literal['king']
    """

    TILE = "tile"
    PAWN = "pawn"
    KING = "king"

    _filepaths = {
        (ColorID.DARK, TILE): ICON_DIRECTORY / "DarkTile.png",
        (ColorID.DARK, PAWN): ICON_DIRECTORY / "DarkPawn.png",
        (ColorID.DARK, KING): ICON_DIRECTORY / "DarkKing.png",
        (ColorID.LIGHT, TILE): ICON_DIRECTORY / "LightTile.png",
        (ColorID.LIGHT, PAWN): ICON_DIRECTORY / "LightPawn.png",
        (ColorID.LIGHT, KING): ICON_DIRECTORY / "LightKing.png",
    }

    def __init__(self, icon_pixel_size: int) -> None:
        self.resolution = (icon_pixel_size, icon_pixel_size)
        self.icons = self._initialize_icons()

    def _initialize_icons(self) -> dict[tuple[ColorID, str], ImageTk.PhotoImage]:
        icons = {}
        for key, path in AssetHandler._filepaths.items():
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
        :return: Image of specific item color
        :rtype: PhotoImage
        """
        key = (color, type)
        return self.icons[key]
