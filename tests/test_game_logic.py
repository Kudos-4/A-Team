"""
tests/test_game_logic.py
Automated tests for game logic acceptance criteria.
Covers ACs: 13.2, 13.3, 13.4, 14.2, 15.1, 15.2, 15.5,
            16.2, 16.3, 17.1, 17.2, 17.3, 18.2, 18.3, 19.1, 19.2, 22.2, 22.3
"""

import unittest
from checkers.game.game import Game
from checkers.game.pieces import Pawn, King
from checkers.colors import ColorID


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_empty_game() -> Game:
    """Return a Game with the board cleared of all pieces."""
    game = Game((8, 8))
    for piece in list(game.dark_pieces + game.light_pieces):
        game._board.remove_piece(piece.position)
    game.pieces[ColorID.DARK].clear()
    game.pieces[ColorID.LIGHT].clear()
    return game


def _add(game: Game, piece) -> None:
    game._board.set_piece(piece.position, piece)
    game.pieces[piece.color].append(piece)


# ---------------------------------------------------------------------------
# AC 13.2, 13.3, 13.4 — Move Highlighting
# ---------------------------------------------------------------------------

class TestMoveHighlighting(unittest.TestCase):

    def test_king_valid_moves_cover_all_four_diagonals(self):
        """AC 13.2: King's valid moves include all four diagonal directions."""
        game = _make_empty_game()
        king = King((4, 4), ColorID.DARK)
        _add(game, king)
        _add(game, Pawn((0, 1), ColorID.LIGHT))   # sentinel to keep game alive
        moves = game.get_valid_moves(king)
        self.assertEqual(set(moves.keys()), {(3, 3), (3, 5), (5, 3), (5, 5)})

    def test_no_valid_moves_when_blocked_by_own_pieces(self):
        """AC 13.3: Pawn with both forward squares occupied by own pieces returns no moves."""
        game = _make_empty_game()
        center = Pawn((4, 4), ColorID.DARK)
        _add(game, center)
        _add(game, Pawn((5, 3), ColorID.DARK))
        _add(game, Pawn((5, 5), ColorID.DARK))
        self.assertEqual(game.get_valid_moves(center), {})

    def test_can_move_to_returns_true_for_valid_destination(self):
        """AC 13.4: can_move_to returns True for a destination shown in get_valid_moves."""
        game = _make_empty_game()
        dark = Pawn((3, 2), ColorID.DARK)
        _add(game, dark)
        _add(game, Pawn((7, 6), ColorID.LIGHT))
        dest = next(iter(game.get_valid_moves(dark)))
        self.assertTrue(game.can_move_to((3, 2), dest))


# ---------------------------------------------------------------------------
# AC 14.2 — Invalid Move: Opponent's Piece
# ---------------------------------------------------------------------------

class TestInvalidMoveOpponent(unittest.TestCase):

    def test_cannot_move_opponents_piece_on_own_turn(self):
        """AC 14.2: can_move_to returns False when trying to move the opponent's piece."""
        game = _make_empty_game()
        light = Pawn((5, 4), ColorID.LIGHT)
        _add(game, light)
        _add(game, Pawn((7, 6), ColorID.DARK))
        # It is DARK's turn; LIGHT piece at (5,4) would normally move to (4,3)
        self.assertFalse(game.can_move_to((5, 4), (4, 3)))


# ---------------------------------------------------------------------------
# AC 15.1, 15.2, 15.5 — King Promotion
# ---------------------------------------------------------------------------

class TestKingPromotion(unittest.TestCase):

    def test_dark_pawn_promotes_at_row_7(self):
        """AC 15.1: Dark pawn reaching row 7 becomes a King."""
        game = _make_empty_game()
        _add(game, Pawn((6, 1), ColorID.DARK))
        _add(game, Pawn((0, 1), ColorID.LIGHT))
        game.move_piece((6, 1), (7, 0))
        self.assertIsInstance(game.get_piece_at((7, 0)), King)
        self.assertTrue(any(isinstance(p, King) for p in game.dark_pieces))

    def test_light_pawn_promotes_at_row_0(self):
        """AC 15.2: Light pawn reaching row 0 becomes a King."""
        game = _make_empty_game()
        _add(game, Pawn((1, 2), ColorID.LIGHT))
        _add(game, Pawn((7, 6), ColorID.DARK))
        game._turn = ColorID.LIGHT
        game.move_piece((1, 2), (0, 1))
        self.assertIsInstance(game.get_piece_at((0, 1)), King)
        self.assertTrue(any(isinstance(p, King) for p in game.light_pieces))

    def test_promotion_mid_jump_ends_turn(self):
        """AC 15.5: When a pawn is promoted during a jump, the turn ends immediately
        even if the resulting King could continue jumping backward."""
        game = _make_empty_game()
        # DARK pawn at (5,2) jumps LIGHT at (6,3) to land at (7,4) and promote.
        # A LIGHT piece at (6,5) would be reachable by the new King going backward,
        # but AC 15.5 requires the turn to end on promotion.
        _add(game, Pawn((5, 2), ColorID.DARK))
        _add(game, Pawn((6, 3), ColorID.LIGHT))
        _add(game, Pawn((6, 5), ColorID.LIGHT))
        game.move_piece((5, 2), (7, 4))
        self.assertEqual(game.turn, ColorID.LIGHT)


# ---------------------------------------------------------------------------
# AC 16.2, 16.3 — Capture Direction Rules
# ---------------------------------------------------------------------------

class TestCaptureDirection(unittest.TestCase):

    def test_pawn_captures_only_forward(self):
        """AC 16.2: Regular pawn can only capture diagonally forward, not backward."""
        game = _make_empty_game()
        dark = Pawn((4, 4), ColorID.DARK)
        _add(game, dark)
        _add(game, Pawn((5, 5), ColorID.LIGHT))   # forward of DARK (row+1)
        _add(game, Pawn((3, 3), ColorID.LIGHT))   # backward of DARK (row-1)
        moves = game.get_valid_moves(dark)
        self.assertIn((6, 6), moves)       # forward capture allowed
        self.assertNotIn((2, 2), moves)    # backward capture not allowed

    def test_king_captures_in_all_four_directions(self):
        """AC 16.3: King can capture opponent pieces in all four diagonal directions."""
        game = _make_empty_game()
        king = King((4, 4), ColorID.DARK)
        _add(game, king)
        for dr, dc in ((1, -1), (1, 1), (-1, -1), (-1, 1)):
            _add(game, Pawn((4 + dr, 4 + dc), ColorID.LIGHT))
        moves = game.get_valid_moves(king)
        captures = [v for v in moves.values() if v is not None]
        self.assertEqual(len(captures), 4)


# ---------------------------------------------------------------------------
# AC 17.1, 17.2, 17.3 — Multi-Jump
# ---------------------------------------------------------------------------

class TestMultiJump(unittest.TestCase):
    """
    Board setup for all three tests:
      DARK pawn at (2,1) can jump LIGHT at (3,2) → land (4,3),
      then jump LIGHT at (5,4) → land (6,5).
    """

    def setUp(self):
        self.game = _make_empty_game()
        self.dark = Pawn((2, 1), ColorID.DARK)
        self.light1 = Pawn((3, 2), ColorID.LIGHT)
        self.light2 = Pawn((5, 4), ColorID.LIGHT)
        _add(self.game, self.dark)
        _add(self.game, self.light1)
        _add(self.game, self.light2)
        # Execute first jump only
        self.game.move_piece((2, 1), (4, 3))

    def test_turn_unchanged_after_first_jump(self):
        """AC 17.1: Turn does not switch while more captures remain available."""
        self.assertEqual(self.game.turn, ColorID.DARK)

    def test_captured_piece_removed_immediately(self):
        """AC 17.2: Captured piece is removed from the board and piece list immediately."""
        self.assertIsNone(self.game.get_piece_at((3, 2)))
        self.assertNotIn(self.light1, self.game.light_pieces)

    def test_turn_switches_when_no_more_captures(self):
        """AC 17.3: Turn switches to opponent once no further captures are possible."""
        self.game.move_piece((4, 3), (6, 5))
        self.assertEqual(self.game.turn, ColorID.LIGHT)


# ---------------------------------------------------------------------------
# AC 18.2, 18.3 — Forced Capture
# ---------------------------------------------------------------------------

class TestForcedCapture(unittest.TestCase):

    def test_jumps_available_when_capture_exists(self):
        """AC 18.2: get_all_jumps is non-empty when a capture move is available."""
        game = _make_empty_game()
        _add(game, Pawn((3, 2), ColorID.DARK))
        _add(game, Pawn((4, 3), ColorID.LIGHT))
        self.assertGreater(len(game.get_all_jumps(ColorID.DARK)), 0)

    def test_regular_move_accepted_when_no_capture_available(self):
        """AC 18.3: can_move_to returns True for a regular move when no jumps exist."""
        game = _make_empty_game()
        _add(game, Pawn((3, 2), ColorID.DARK))
        _add(game, Pawn((7, 6), ColorID.LIGHT))
        self.assertFalse(game.get_all_jumps(ColorID.DARK))
        self.assertTrue(game.can_move_to((3, 2), (4, 1)))


# ---------------------------------------------------------------------------
# AC 19.1, 19.2 — Game End Conditions
# ---------------------------------------------------------------------------

class TestGameEnd(unittest.TestCase):

    def test_winner_when_opponent_has_no_pieces(self):
        """AC 19.1: Winner declared immediately when all opponent pieces are captured."""
        game = _make_empty_game()
        _add(game, Pawn((4, 4), ColorID.DARK))
        # LIGHT has no pieces → DARK wins
        self.assertEqual(game.get_game_winner(), ColorID.DARK)

    def test_winner_when_opponent_has_no_legal_moves(self):
        """AC 19.2: Winner declared when one player has no legal moves remaining."""
        game = _make_empty_game()
        # DARK pawn at row 7: forward direction is row 8 (out of bounds) → no moves
        _add(game, Pawn((7, 6), ColorID.DARK))
        # LIGHT at row 3 has valid moves to row 2 (empty board)
        _add(game, Pawn((3, 4), ColorID.LIGHT))
        # get_game_winner checks LIGHT first (has moves), then DARK (no moves) → LIGHT wins
        self.assertEqual(game.get_game_winner(), ColorID.LIGHT)


# ---------------------------------------------------------------------------
# AC 22.2, 22.3 — Turn Indicator Behaviour
# ---------------------------------------------------------------------------

class TestTurnIndicator(unittest.TestCase):

    def test_turn_switches_after_regular_move(self):
        """AC 22.2: Turn indicator updates to the opponent after a valid move."""
        game = _make_empty_game()
        _add(game, Pawn((3, 2), ColorID.DARK))
        _add(game, Pawn((7, 6), ColorID.LIGHT))
        self.assertEqual(game.turn, ColorID.DARK)
        game.move_piece((3, 2), (4, 1))
        self.assertEqual(game.turn, ColorID.LIGHT)

    def test_turn_unchanged_mid_multijump(self):
        """AC 22.3: Turn only updates after the entire multi-jump sequence finishes."""
        game = _make_empty_game()
        _add(game, Pawn((2, 1), ColorID.DARK))
        _add(game, Pawn((3, 2), ColorID.LIGHT))
        _add(game, Pawn((5, 4), ColorID.LIGHT))
        game.move_piece((2, 1), (4, 3))
        self.assertEqual(game.turn, ColorID.DARK)   # mid-sequence: still DARK
        game.move_piece((4, 3), (6, 5))
        self.assertEqual(game.turn, ColorID.LIGHT)  # sequence done: switched


if __name__ == "__main__":
    unittest.main(verbosity=2)
