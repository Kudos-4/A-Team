"""
Usage:
    python tests/testCases.py           # Run all tests
    python tests/testCases.py --menu    # Choose specific tests via menu
"""

import os
import sys
import unittest

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TESTS_DIR)
# Project root → allows 'import checkers'; tests dir → allows sibling test imports
for _p in (_PROJECT_ROOT, _TESTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from checkers.game.board import Board
from checkers.game.pieces import Pawn, King
from checkers.game.game import Game
from checkers.constants.colors import ColorID

# New test modules
from test_game_logic import (
    TestMoveHighlighting,
    TestInvalidMoveOpponent,
    TestKingPromotion,
    TestCaptureDirection,
    TestMultiJump,
    TestForcedCapture,
    TestGameEnd,
    TestTurnIndicator,
)
from test_auth_db import (
    TestRegistrationErrorMessage,
    TestDuplicateRegistration,
    TestLoginInvalidCredentials,
    TestGameRecordDatabase,
)
from test_pve_logic import (
    TestForcedCaptureLogic,
    TestPvEComputer,
)


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
        self.assertEqual(len(self.game.dark_pieces), 12)

    def test_number_of_white_pieces(self):
        self.assertEqual(len(self.game.light_pieces), 12)

    def test_pieces_on_black_squares(self):
        all_pieces = self.game.dark_pieces + self.game.light_pieces
        self.assertTrue(
            all(
                _is_black_square(self.game._board.cols, p.position)
                for p in all_pieces
            )
        )

    def test_wrong_piece_position_detected(self):
        all_pieces = self.game.dark_pieces + self.game.light_pieces
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

_loader = unittest.TestLoader()

def _suite(*classes):
    combined = unittest.TestSuite()
    for cls in classes:
        combined.addTests(_loader.loadTestsFromTestCase(cls))
    return combined

SUITES = {
    # --- Original suites (fixed) ---
    "1": ("Pieces (AC 13.1, 15.4)",
          _suite(TestPieces)),
    "2": ("Board (AC 12.1–12.4, 14.1)",
          _suite(TestBoard)),
    "3": ("Game – Initialisation (AC 10.2, 12.2–12.3)",
          _suite(TestGame)),
    # --- New: game logic ---
    "4": ("Game Logic – Highlighting & Selection (AC 13.2, 13.3, 13.4, 14.2)",
          _suite(TestMoveHighlighting, TestInvalidMoveOpponent)),
    "5": ("Game Logic – King Promotion (AC 15.1, 15.2, 15.5)",
          _suite(TestKingPromotion)),
    "6": ("Game Logic – Capture Direction (AC 16.2, 16.3)",
          _suite(TestCaptureDirection)),
    "7": ("Game Logic – Multi-Jump (AC 17.1, 17.2, 17.3)",
          _suite(TestMultiJump)),
    "8": ("Game Logic – Forced Capture & Game End (AC 18.2, 18.3, 19.1, 19.2)",
          _suite(TestForcedCapture, TestGameEnd)),
    "9": ("Game Logic – Turn Indicator (AC 22.2, 22.3)",
          _suite(TestTurnIndicator)),
    # --- New: auth & database ---
    "10": ("Auth – Registration Errors (AC 1.3)",
           _suite(TestRegistrationErrorMessage)),
    "11": ("Auth – Duplicate Check (AC 3.1, 3.2)",
           _suite(TestDuplicateRegistration)),
    "12": ("Auth – Login Validation (AC 7.1)",
           _suite(TestLoginInvalidCredentials)),
    "13": ("Database – Game Records (AC 20.2, 20.3, 23.3, 30.1, 30.2)",
           _suite(TestGameRecordDatabase)),
    # --- New: PvE / computer opponent ---
    "14": ("PvE – Forced Capture Logic (AC 26.2)",
           _suite(TestForcedCaptureLogic)),
    "15": ("PvE – Computer & Minimax (AC 26.1, 26.3, 27.1, 29.1–29.3)",
           _suite(TestPvEComputer)),
}


def run_suite(label: str, suite: unittest.TestSuite) -> unittest.TestResult:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    return runner.run(suite)


def menu() -> None:
    print("\nSelect a test group to run:")
    for key, (label, _) in SUITES.items():
        print(f"  {key:>2}. {label}")
    print("   0. Exit")

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
    print("\n" + "=" * 60)
    print("  A-TEAM CHECKERS — Full Automated Test Suite")
    print("=" * 60)

    total_run = total_failures = total_errors = 0

    for label, suite in SUITES.values():
        result = run_suite(label, suite)
        total_run      += result.testsRun
        total_failures += len(result.failures)
        total_errors   += len(result.errors)

    passed = total_run - total_failures - total_errors
    status = "ALL PASSED" if (total_failures + total_errors) == 0 else "SOME FAILURES"
    print("\n" + "=" * 60)
    print(f"  {status}")
    print(f"  Total: {total_run}  |  Passed: {passed}  |  "
          f"Failed: {total_failures}  |  Errors: {total_errors}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    if "--menu" in sys.argv:
        menu()
    else:
        run_all()
