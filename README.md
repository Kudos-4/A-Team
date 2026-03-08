# A-Team Checkers Game
American checkers game implemented in Python 3.12 and tested with pytest.


## Creating Tests
All tests are ran in the tests folder with each test in its own file.
Per Pytest's default configuration, all files must start with test_*.py or \*_test.py. All functions meant to be tested need to start with test\_ (e.g. test_piece_is_king).

Pytest requires a \_\_init__.py in the test folder to properly locate it.

To run all test, type this into the command line (make sure you're in root directory):
```bash
  pytest
```
## Structure

All production code goes into the checkers folder. Games, UI, and database control should be in separate folders. main.py should be the injection point to the menu.

All files in checkers are treated like packages. They cannot be run with Python; ```python checkers/game/pieces.py``` won't work. If you want to run it directly, use:

 ```python -m checkers.game.pieces``` (use dots and no .py at the end).
 
 Or you could have another Python file in the source directory, import it, and run the Python file regularly.
