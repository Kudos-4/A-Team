"""Main injection for running game in UI"""

from checkers.game.game import Game
# from checkers.user_interface.ui import UserInterface <- something similar


def main() -> None:
    """Main runs UI function, UI imports game to display and interact with"""
    size = (8, 8)
    game = Game(size)


if __name__ == "__main__":
    main()
