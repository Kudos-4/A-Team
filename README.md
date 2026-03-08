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

All production code goes into the checkers folder. Games, UI, and database control should in separate folders. main.py (in checkers) should be the injection point to the menu.
