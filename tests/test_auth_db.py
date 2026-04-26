"""
tests/test_auth_db.py
Automated tests for authentication and database acceptance criteria.
Covers ACs: 1.3, 3.1, 3.2, 7.1, 20.2, 20.3, 23.3, 30.1, 30.2
Uses a temporary SQLite file so the production database is never touched.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from checkers.auth.auth_logic import validate_register_fields


# ---------------------------------------------------------------------------
# AC 1.3 — Registration error message for invalid input
# ---------------------------------------------------------------------------

class TestRegistrationErrorMessage(unittest.TestCase):

    def test_invalid_input_returns_error_string(self):
        """AC 1.3: Submitting invalid registration data returns a non-empty error message."""
        error = validate_register_fields("u", "not-an-email", "weak", "weak")
        self.assertIsNotNone(error)
        self.assertIsInstance(error, str)
        self.assertGreater(len(error), 0)

    def test_valid_input_returns_no_error(self):
        """AC 1.3 (counter): Valid input produces no error message."""
        error = validate_register_fields("validuser", "user@example.com", "Test@1234", "Test@1234")
        self.assertIsNone(error)


# ---------------------------------------------------------------------------
# Shared DB fixture
# ---------------------------------------------------------------------------

class _TempDbTestCase(unittest.TestCase):
    """Base class that wires every test method to a fresh temporary SQLite DB."""

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        self._patcher = patch("checkers.auth.database.DB_PATH", self.db_path)
        self._patcher.start()
        from checkers.auth.database import init_db
        init_db()

    def tearDown(self):
        self._patcher.stop()
        try:
            os.unlink(self.db_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# AC 3.1, 3.2 — Duplicate registration check
# ---------------------------------------------------------------------------

class TestDuplicateRegistration(_TempDbTestCase):

    def test_duplicate_email_rejected(self):
        """AC 3.1: Registering with an already-used email address returns an error."""
        from checkers.auth.auth import register_user
        register_user("user1", "shared@example.com", "Test@1234")
        success, msg = register_user("user2", "shared@example.com", "Test@1234")
        self.assertFalse(success)
        self.assertIn("email", msg.lower())

    def test_duplicate_username_rejected(self):
        """AC 3.2: Registering with an already-taken username returns an error."""
        from checkers.auth.auth import register_user
        register_user("sameuser", "first@example.com", "Test@1234")
        success, msg = register_user("sameuser", "second@example.com", "Test@1234")
        self.assertFalse(success)
        self.assertIn("username", msg.lower())

    def test_unique_credentials_accepted(self):
        """AC 3.1/3.2 (counter): Unique username and email registers successfully."""
        from checkers.auth.auth import register_user
        success, msg = register_user("uniqueuser", "unique@example.com", "Test@1234")
        self.assertTrue(success)
        self.assertEqual(msg, "")


# ---------------------------------------------------------------------------
# AC 7.1 — Login with invalid credentials
# ---------------------------------------------------------------------------

class TestLoginInvalidCredentials(_TempDbTestCase):

    def setUp(self):
        super().setUp()
        from checkers.auth.auth import register_user
        register_user("logintest", "login@example.com", "Test@1234")

    def test_wrong_password_returns_none(self):
        """AC 7.1: Login with a wrong password returns None (rejected)."""
        from checkers.auth.auth import login_user
        result = login_user("logintest", "WrongPass@99")
        self.assertIsNone(result)

    def test_nonexistent_user_returns_none(self):
        """AC 7.1: Login with a username that does not exist returns None."""
        from checkers.auth.auth import login_user
        result = login_user("nobody", "Test@1234")
        self.assertIsNone(result)

    def test_correct_credentials_return_username(self):
        """AC 7.1 (counter): Login with correct credentials returns the username."""
        from checkers.auth.auth import login_user
        result = login_user("logintest", "Test@1234")
        self.assertEqual(result, "logintest")


# ---------------------------------------------------------------------------
# AC 20.2, 20.3, 23.3, 30.1, 30.2 — Game record persistence
# ---------------------------------------------------------------------------

class TestGameRecordDatabase(_TempDbTestCase):

    def setUp(self):
        super().setUp()
        from checkers.auth.auth import register_user
        from checkers.auth.database import get_user_id
        register_user("player1", "p1@example.com", "Test@1234")
        self.user_id = get_user_id("player1")

    def test_save_game_stores_complete_record(self):
        """AC 20.2: save_game persists opponent, result, move count, date, and moves."""
        from checkers.auth.database import save_game, get_game_history
        moves = ["1-2", "23-14", "5-6"]
        save_game(self.user_id, "Alice", "Win", 6, "2024-01-15 10:30:00", moves)
        history = get_game_history(self.user_id)
        self.assertEqual(len(history), 1)
        rec = history[0]
        self.assertEqual(rec["opponent"], "Alice")
        self.assertEqual(rec["result"], "Win")
        self.assertEqual(rec["total_moves"], 6)
        self.assertEqual(rec["date"], "2024-01-15")
        self.assertEqual(rec["moves"], moves)

    def test_saved_game_appears_in_history(self):
        """AC 20.3 / 23.3: A saved game record is visible in get_game_history."""
        from checkers.auth.database import save_game, get_game_history
        save_game(self.user_id, "Bob", "Loss", 10, "2024-02-01 09:00:00", [])
        history = get_game_history(self.user_id)
        self.assertTrue(any(g["opponent"] == "Bob" for g in history))

    def test_pve_game_saved_with_computer_opponent(self):
        """AC 30.1: PvE game result is stored with opponent name 'Computer'."""
        from checkers.auth.database import save_game, get_game_history
        save_game(self.user_id, "Computer", "Win", 20, "2024-03-01 14:00:00", [])
        history = get_game_history(self.user_id)
        self.assertEqual(history[0]["opponent"], "Computer")

    def test_pve_win_and_loss_results_stored_correctly(self):
        """AC 30.2: PvE results are saved as 'Win' when player wins and 'Loss' when computer wins."""
        from checkers.auth.database import save_game, get_game_history
        save_game(self.user_id, "Computer", "Win",  15, "2024-03-01 14:00:00", [])
        save_game(self.user_id, "Computer", "Loss",  8, "2024-03-01 15:00:00", [])
        history = get_game_history(self.user_id)
        results = {g["result"] for g in history}
        self.assertIn("Win", results)
        self.assertIn("Loss", results)

    def test_multiple_games_all_appear_in_history(self):
        """AC 20.3: Each completed game creates a separate history entry."""
        from checkers.auth.database import save_game, get_game_history
        save_game(self.user_id, "Alice", "Win",  5, "2024-04-01 10:00:00", [])
        save_game(self.user_id, "Bob",   "Loss", 8, "2024-04-02 11:00:00", [])
        history = get_game_history(self.user_id)
        self.assertEqual(len(history), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
