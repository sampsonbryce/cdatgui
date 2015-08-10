# CDATGUI

This is a refactor/rethinking of the existing UV-CDAT GUI. We're porting things over to PySide, rather than being in PyQt, and working on detangling the existing spreadsheet/VCS integration and integrating it into a new shell.

## Development Requirements

The current requirements are:

1. A recent version of UV-CDAT (installed from source) (>2.2, due to vcs.prefix -> vcs.sample_data changeover)
2. `PySide` (might give you some lip when you install it; installation issues will get ironed out, I wound up having to use homebrew to install it, and added a .pth file to UV-CDAT's site-packages directory that points to homebrew's site-packages).
3. `pytest` (installable via pip, used to run tests) 
4. `pytest-qt` (used to power GUI tests)
5. `pytest-cov` (used to measure test coverage)

## Installation

Once you have the requirements installed, you should be able to do this:

1. `source uvcdat/bin/setup_runtime.sh`
2. `cd cdatgui`
3. `python setup.py install`
4. `cdatgui`

This should get you the current rev of the GUI up and running.

## Running tests

To run tests and generate an HTML report listing the current coverage status, you should be able to just use the script in the root of the project, `test`. It will run all of the tests, generate a coverage report, and shove that into `htmlcov`. To view the results of the coverage, open `htmlcov/index.html`.
