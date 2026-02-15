PYTHON := python3
PIP    := pip3

MAIN   := a_maze_ing.py
CONFIG := config.txt

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	@find . -type d -name "__pycache__" -print -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache
	@rm -f *.pyc
	@rm -f maze.txt

lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
