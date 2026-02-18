# **************************************************************************** #
#                                  A-Maze-ing                                  #
# **************************************************************************** #

PYTHON      := python3
MAIN        := a_maze_ing.py
CONFIG      := config.txt

FLAKE8      := flake8
MYPY        := mypy

MYPY_FLAGS  := --warn-return-any \
               --warn-unused-ignores \
               --ignore-missing-imports \
               --disallow-untyped-defs \
               --check-untyped-defs

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .mypy_cache .pytest_cache
	rm -rf *.pyc */*.pyc */*/*.pyc

lint:
	$(FLAKE8) .
	$(MYPY) . $(MYPY_FLAGS)

lint-strict:
	$(FLAKE8) .
	$(MYPY) . --strict
