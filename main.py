"""Main injection for running game in UI"""

from checkers.user_interface import MainMenuUI
from checkers.auth import database


def main() -> None:
    """
    Main runs UI function, UI imports game to display and interact with.
    Called init_db() from /auth/database.py before UI, ensure db connection.
    """
    database.init_db()
    RESOLUTION = (1920, 1080)
    ui = MainMenuUI(RESOLUTION)
    ui.mainloop()


if __name__ == "__main__":
    main()
