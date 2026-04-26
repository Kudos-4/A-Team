"""
tests/test_pve_logic.py
Automated tests for the PvE / computer-opponent acceptance criteria.
Covers ACs: 26.1, 26.2, 26.3, 27.1, 29.1, 29.2, 29.3

The MockGameUI satisfies GameMode's dependency on game_ui without opening any
Tkinter windows; only .game, .after(), and .update_interface() are needed.
"""

import unittest

from checkers.game.game import Game
from checkers.game.pieces import Pawn, King
from checkers.constants.colors import ColorID
from checkers.user_interface.player import Player
from checkers.gamemodes.pve import PvEGameMode, GameState


# ---------------------------------------------------------------------------
# Minimal mock — no Tkinter required
# ---------------------------------------------------------------------------

class MockGameUI:
    def __init__(self, game: Game) -> None:
        self.game = game

    def after(self, *args, **kwargs) -> None:   # replaces tk.after scheduling
        pass

    def update_interface(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Helpers (same as test_game_logic.py but duplicated to keep files independent)
# ---------------------------------------------------------------------------

def _make_empty_game() -> Game:
    game = Game((8, 8))
    for piece in list(game.dark_pieces + game.light_pieces):
        game._board.remove_piece(piece.position)
    game.pieces[ColorID.DARK].clear()
    game.pieces[ColorID.LIGHT].clear()
    return game


def _add(game: Game, piece) -> None:
    game._board.set_piece(piece.position, piece)
    game.pieces[piece.color].append(piece)


def _make_pve(game: Game) -> PvEGameMode:
    """Create a PvEGameMode where the human plays DARK and computer plays LIGHT.
    DARK moves first so the computer's __init__ branch (_make_move) is skipped."""
    mock_ui = MockGameUI(game)
    player1 = Player(username="human",    color=ColorID.DARK)
    player2 = Player(username="computer", color=ColorID.LIGHT, is_computer=True)
    return PvEGameMode(mock_ui, (player1, player2))


# ---------------------------------------------------------------------------
# AC 26.2 — Forced capture at the game-logic level
# (all_moves_of_color returns only jumps when a jump is available)
# ---------------------------------------------------------------------------

class TestForcedCaptureLogic(unittest.TestCase):

    def test_all_moves_returns_only_jumps_when_capture_available(self):
        """AC 26.2: When a capture is available, the computer (and game) returns
        only capturing moves — regular moves are suppressed."""
        game = _make_empty_game()
        _add(game, Pawn((3, 2), ColorID.DARK))
        _add(game, Pawn((4, 3), ColorID.LIGHT))
        game._turn = ColorID.LIGHT
        moves = game.all_moves_of_color(ColorID.LIGHT)
        # Only one move: LIGHT jumps DARK at (3,2) to land at (2,1)
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0], ((4, 3), (2, 1)))

    def test_regular_moves_returned_when_no_capture_available(self):
        """AC 26.2 (counter): Regular moves returned when no jump exists."""
        game = _make_empty_game()
        _add(game, Pawn((4, 3), ColorID.LIGHT))
        _add(game, Pawn((7, 6), ColorID.DARK))
        game._turn = ColorID.LIGHT
        moves = game.all_moves_of_color(ColorID.LIGHT)
        self.assertGreater(len(moves), 0)
        # None of them should be jumps
        for from_pos, to_pos in moves:
            piece = game.get_piece_at(from_pos)
            valid = game.get_valid_moves(piece)
            self.assertIsNone(valid.get(to_pos))   # None = regular move, not a capture


# ---------------------------------------------------------------------------
# AC 26.1, 26.3, 27.1, 29.1, 29.2, 29.3 — PvEGameMode / minimax
# ---------------------------------------------------------------------------

class TestPvEComputer(unittest.TestCase):

    def setUp(self):
        """Full initial board; human=DARK (moves first) so __init__ skips _make_move."""
        self.game = Game((8, 8))
        self.mock_ui = MockGameUI(self.game)
        self.pve = _make_pve(self.game)

    # --- AC 26.1 -----------------------------------------------------------

    def test_computer_returns_nonempty_best_moves(self):
        """AC 26.1: Computer selects at least one valid move on its turn."""
        self.game._turn = ColorID.LIGHT
        best = self.pve._compute_best_moves()
        self.assertGreater(len(best), 0)

    def test_computer_moves_are_all_valid(self):
        """AC 26.1: Every move returned by _compute_best_moves is a legal move."""
        self.game._turn = ColorID.LIGHT
        best = self.pve._compute_best_moves()
        for from_pos, to_pos in best:
            self.assertTrue(self.game.can_move_to(from_pos, to_pos))

    # --- AC 26.3 -----------------------------------------------------------

    def test_score_favors_more_computer_pieces(self):
        """AC 26.3: _score_by_piece_value is higher when the computer has more pieces."""
        # Equal 12v12 board → score = computer_value - player_value = 12 - 12 = 0
        gs_equal = GameState(self.mock_ui)
        score_equal = self.pve._score_by_piece_value(gs_equal)

        # Board with only 1 LIGHT (computer) piece and 0 DARK pieces → score = 1 - 0 = 1
        game_adv = _make_empty_game()
        _add(game_adv, Pawn((4, 4), ColorID.LIGHT))
        mock_adv = MockGameUI(game_adv)
        pve_adv = _make_pve(game_adv)
        gs_adv = GameState(mock_adv)
        score_adv = pve_adv._score_by_piece_value(gs_adv)

        self.assertGreater(score_adv, score_equal)

    def test_score_penalises_fewer_computer_pieces(self):
        """AC 26.3: Score is negative when the computer has fewer pieces than the player."""
        # 1 DARK (player) piece, 0 LIGHT (computer) pieces → score = 0 - 1 = -1
        game_adv = _make_empty_game()
        _add(game_adv, Pawn((4, 4), ColorID.DARK))
        mock_adv = MockGameUI(game_adv)
        pve_adv = _make_pve(game_adv)
        gs_adv = GameState(mock_adv)
        score = pve_adv._score_by_piece_value(gs_adv)
        self.assertLess(score, 0)

    def test_king_adds_extra_value_to_score(self):
        """AC 26.3: A King counts as 2 in the score (piece + king bonus)."""
        game_king = _make_empty_game()
        _add(game_king, King((4, 4), ColorID.LIGHT))   # value = 1 piece + 1 king = 2
        _add(game_king, Pawn((3, 3), ColorID.DARK))    # value = 1 piece
        mock_king = MockGameUI(game_king)
        pve_king = _make_pve(game_king)
        gs_king = GameState(mock_king)
        score = pve_king._score_by_piece_value(gs_king)
        self.assertEqual(score, 1)   # 2 (computer) - 1 (player) = 1

    # --- AC 27.1 -----------------------------------------------------------

    def test_input_ignored_during_computer_turn(self):
        """AC 27.1: tile_pressed does nothing while it is the computer's turn."""
        game = _make_empty_game()
        _add(game, Pawn((3, 2), ColorID.DARK))
        _add(game, Pawn((5, 4), ColorID.LIGHT))
        game._turn = ColorID.LIGHT
        mock_ui = MockGameUI(game)
        pve = _make_pve(game)
        selected_before = pve.get_selected()
        pve.tile_pressed((3, 2))   # player tries to interact on computer's turn
        self.assertEqual(pve.get_selected(), selected_before)

    # --- AC 29.1, 29.2, 29.3 -----------------------------------------------

    def test_minimax_returns_integer_at_depth_zero(self):
        """AC 29.1: _minimax at depth 0 evaluates the leaf and returns an integer."""
        gs = GameState(self.mock_ui)
        score = self.pve._minimax(gs, 0)
        self.assertIsInstance(score, int)

    def test_minimax_returns_integer_at_depth_two(self):
        """AC 29.1/29.2: _minimax looks ahead two plies without crashing."""
        gs = GameState(self.mock_ui)
        score = self.pve._minimax(gs, 2)
        self.assertIsInstance(score, int)

    def test_minimax_picks_capture_over_regular_move(self):
        """AC 29.3: With depth>0, minimax picks the best-scoring move (captures score higher)."""
        # LIGHT at (4,3) can either move regularly to (3,4) or capture DARK at (3,2) → (2,1).
        # Capturing removes a DARK piece, raising the score; minimax should prefer it.
        game = _make_empty_game()
        _add(game, Pawn((3, 2), ColorID.DARK))
        _add(game, Pawn((4, 3), ColorID.LIGHT))
        game._turn = ColorID.LIGHT
        mock_ui = MockGameUI(game)
        pve = _make_pve(game)
        best = pve._compute_best_moves()
        # The only available move is the jump (forced capture), so it must be returned
        self.assertEqual(len(best), 1)
        self.assertEqual(best[0], ((4, 3), (2, 1)))

    def test_compute_best_moves_all_have_equal_score(self):
        """AC 29.3: _compute_best_moves returns a list; all entries share the highest score."""
        self.game._turn = ColorID.LIGHT
        best = self.pve._compute_best_moves()
        # Verify every returned move produces the same minimax score
        scores = set()
        for move in best:
            gs_copy = self.pve._new_gamestate(self.pve._gamestate, move)
            scores.add(self.pve._minimax(gs_copy, self.pve.max_depth))
        self.assertEqual(len(scores), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
