"""Main injection for running game in UI"""

from checkers.user_interface.ui import CheckersUserInterface


def main() -> None:
    """Main runs UI function, UI imports game to display and interact with"""
    RESOLUTION = (1920, 1080)
    ui = CheckersUserInterface(RESOLUTION)
    ui.mainloop()


if __name__ == "__main__":
    main()
