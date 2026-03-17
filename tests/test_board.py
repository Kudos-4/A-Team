import pytest

from checkers.game.board import Board
from checkers.constants.colors import ColorID


@pytest.fixture
def board() -> Board:
    return Board(board_size=(8, 8))


def test_board_size(board: Board) -> None:
    row_lengths = map(len, board._board)
    assert all(length == 8 for length in row_lengths)
    column_lengths = map(len, (row for row in board._board))
    assert all(length == 8 for length in column_lengths)


def test_alternating_colors(board: Board) -> None:
    for row in range(board.rows):
        current_color = ColorID((row % 2) ^ 1)
        for col in range(board.cols):
            tile = board._tile_at(position=(row, col))
            assert tile.color == current_color
            current_color = ~current_color
