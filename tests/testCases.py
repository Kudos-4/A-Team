"""
Usage:
    python run_tests.py          # Run all tests
    python run_tests.py --menu   # Choose specific tests via menu
"""

import sys
import unittest

from checkers.game.board import Board
from checkers.game.pieces import Pawn, King
from checkers.game.game import Game
from checkers.colors import ColorID


# ---------------------------------------------------------------------------
#                           Pieces Tests
# ---------------------------------------------------------------------------


class TestPieces(unittest.TestCase):
    def setUp(self):
        self.white_pawn = Pawn(_position=(0, 0), _color=ColorID.LIGHT)
        self.black_pawn = Pawn(_position=(0, 4), _color=ColorID.DARK)
        self.white_king = King(_position=(1, 2), _color=ColorID.LIGHT)
        self.black_king = King(_position=(1, 2), _color=ColorID.DARK)

    def test_king_not_pawn(self):
        king = King((0, 0), ColorID.DARK)
        self.assertNotIsInstance(king, Pawn)

    def test_white_pawn_moveset(self):
        self.assertEqual(self.white_pawn.moveset, ((-1, -1), (-1, 1)))

    def test_black_pawn_moveset(self):
        self.assertEqual(self.black_pawn.moveset, ((1, -1), (1, 1)))

    def test_king_moveset(self):
        oracle = ((1, -1), (1, 1), (-1, -1), (-1, 1))
        self.assertEqual(self.white_king.moveset, oracle)
        self.assertEqual(self.black_king.moveset, oracle)

    def test_raise_on_set_color(self):
        with self.assertRaises(AttributeError):
            self.white_pawn.color = ColorID.DARK
        with self.assertRaises(AttributeError):
            self.black_king.color = ColorID.LIGHT

    def test_raise_on_set_moveset(self):
        with self.assertRaises(AttributeError):
            self.black_pawn.moveset = ((1, -1), (1, 1))
        with self.assertRaises(AttributeError):
            self.white_king.moveset = ((1, -1), (1, 1))


# ---------------------------------------------------------------------------
#                              Board Tests
# ---------------------------------------------------------------------------


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(board_size=(8, 8))

    def test_board_size(self):
        row_lengths = [len(row) for row in self.board._board]
        self.assertTrue(all(length == 8 for length in row_lengths))

    def test_alternating_colors(self):
        for row in range(self.board.rows):
            current_color = ColorID((row % 2) ^ 1)
            for col in range(self.board.cols):
                tile = self.board._tile_at(position=(row, col))
                self.assertEqual(tile.color, current_color)
                current_color = ~current_color

    def test_set_piece(self):
        pawn = Pawn(_position=(0, 1), _color=ColorID.DARK)
        self.board.set_piece((0, 1), pawn)
        self.assertEqual(self.board.piece_at((0, 1)), pawn)

    def test_set_piece_occupied_raises(self):
        pawn = Pawn(_position=(0, 1), _color=ColorID.DARK)
        self.board.set_piece((0, 1), pawn)
        with self.assertRaises(ValueError):
            self.board.set_piece((0, 1), pawn)

    def test_move_piece(self):
        pawn = Pawn(_position=(0, 1), _color=ColorID.DARK)
        self.board.set_piece((0, 1), pawn)
        self.board.move_piece((0, 1), (1, 2))
        self.assertIsNone(self.board.piece_at((0, 1)))
        self.assertEqual(self.board.piece_at((1, 2)), pawn)

    def test_move_piece_updates_position(self):
        pawn = Pawn(_position=(0, 1), _color=ColorID.DARK)
        self.board.set_piece((0, 1), pawn)
        self.board.move_piece((0, 1), (1, 2))
        self.assertEqual(pawn.position, (1, 2))

    def test_move_from_empty_raises(self):
        with self.assertRaises(ValueError):
            self.board.move_piece((0, 0), (1, 1))

    def test_move_to_occupied_raises(self):
        pawn_a = Pawn(_position=(0, 1), _color=ColorID.DARK)
        pawn_b = Pawn(_position=(1, 2), _color=ColorID.LIGHT)
        self.board.set_piece((0, 1), pawn_a)
        self.board.set_piece((1, 2), pawn_b)
        with self.assertRaises(ValueError):
            self.board.move_piece((0, 1), (1, 2))


# ---------------------------------------------------------------------------
#                             Game Tests
# ---------------------------------------------------------------------------


def _is_black_square(cols: int, position: tuple) -> bool:
    row, col = position
    start = (row % 2) ^ 1
    return col in range(start, cols, 2)


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(board_size=(8, 8))

    def test_number_of_black_pieces(self):
        self.assertEqual(len(self.game._black_pieces), 12)

    def test_number_of_white_pieces(self):
        self.assertEqual(len(self.game._white_pieces), 12)

    def test_pieces_on_black_squares(self):
        all_pieces = self.game._black_pieces + self.game._white_pieces
        self.assertTrue(
            all(
                _is_black_square(self.game._board.cols, p.position)
                for p in all_pieces
            )
        )

    def test_wrong_piece_position_detected(self):
        all_pieces = self.game._black_pieces + self.game._white_pieces
        all_pieces[0]._position = (0, 0)  # Force onto a white square
        self.assertFalse(
            all(
                _is_black_square(self.game._board.cols, p.position)
                for p in all_pieces
            )
        )

    def test_initial_turn_is_black(self):
        self.assertEqual(self.game._turn, ColorID.DARK)


# ---------------------------------------------------------------------------
# Menu + Runner
# ---------------------------------------------------------------------------

SUITES = {
    "1": ("Pieces", unittest.TestLoader().loadTestsFromTestCase(TestPieces)),
    "2": ("Board", unittest.TestLoader().loadTestsFromTestCase(TestBoard)),
    "3": ("Game", unittest.TestLoader().loadTestsFromTestCase(TestGame)),
}


def run_suite(label: str, suite: unittest.TestSuite) -> None:
    print(f"\n{'=' * 50}")
    print(f"  Running: {label}")
    print(f"{'=' * 50}")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


def menu() -> None:
    print("\nSelect a test group to run:")
    for key, (label, _) in SUITES.items():
        print(f"  {key}. {label}")
    print("  0. Exit")

    choice = input("\nEnter choice: ").strip()
    if choice == "0":
        print("Exiting.")
        return
    if choice in SUITES:
        label, suite = SUITES[choice]
        run_suite(label, suite)
    else:
        print("Invalid choice.")


def run_all() -> None:
    all_suites = unittest.TestSuite(suite for _, suite in SUITES.values())
    print("\nRunning all tests...\n")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(all_suites)


if __name__ == "__main__":
    if "--menu" in sys.argv:
        menu()
    else:
        run_all()
