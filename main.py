"""Main injection for running game in UI"""

from checkers.user_interface.ui import CheckersUserInterface
from checkers.auth.database import init_db

def main() -> None:
    """
    Main runs UI function, UI imports game to display and interact with.
    Called init_db() from /auth/database.py before UI, ensure db connection.
    """
    init_db()
    RESOLUTION = (1920, 1080)
    ui = CheckersUserInterface(RESOLUTION)
    ui.mainloop()


if __name__ == "__main__":
    main()
