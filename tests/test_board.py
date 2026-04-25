import pytest

from checkers.colors import ColorID
from checkers.game import Game, Board, Pawn


@pytest.fixture
def empty_board() -> Board:
    return Board(board_size=(8, 8))


@pytest.fixture
def initial_board() -> Board:
    return Game(board_size=(8, 8))._board


def test_board_size(empty_board: Board) -> None:
    row_lengths = map(len, empty_board._board)
    assert all(length == 8 for length in row_lengths)
    column_lengths = map(len, (row for row in empty_board._board))
    assert all(length == 8 for length in column_lengths)


def test_tile_colors(empty_board: Board) -> None:
    for row in range(empty_board.rows):
        current_color = ColorID((row % 2) ^ 1)
        for col in range(empty_board.cols):
            tile = empty_board._tile_at(position=(row, col))
            assert tile.color == current_color
            current_color = ~current_color


def test_tile_notation(empty_board: Board) -> None:
    notation_count = 0
    for row in empty_board._board:
        for tile in row:
            if tile.color:
                assert not tile.notation
                continue
            notation_count += 1
            assert tile.notation == notation_count


def test_set_on_empty(initial_board: Board) -> None:
    position = (0, 0)
    piece = Pawn(position, ColorID.DARK)
    initial_board.set_piece((0, 0), piece)
    assert initial_board[position]


def test_set_on_occupied(initial_board: Board) -> None:
    existing_location = (0, 1)
    piece = Pawn(existing_location, ColorID.DARK)
    with pytest.raises(ValueError):
        initial_board.set_piece(existing_location, piece)


def test_valid_move_state(initial_board: Board) -> None:
    initial = (2, 1)
    target = (3, 0)
    initial_board.move_piece(initial, target)
    assert not initial_board[initial]
    assert initial_board[target]

def test_move_from_empty(initial_board: Board) -> None:
    empty_cell = (2, 2)
    black_cell = (3, 4)
    with pytest.raises(ValueError):
        initial_board.move_piece(empty_cell, black_cell)

def test_move_to_empty(initial_board: Board) -> None:
    valid_cell = (0, 1)
    empty_cell = (1, 2)
    with pytest.raises(ValueError):
        initial_board.move_piece(valid_cell, empty_cell)
