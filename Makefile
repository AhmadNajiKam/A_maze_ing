install:
	uv sync

build:
	uv build --wheel --out-dir .

run:
	uv run python a_maze_ing.py config.txt

debug:
	uv run python -m pdb a_maze_ing.py config.txt

lint:
	uv run flake8 .
	uv run mypy . \
		--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

clean:
	find . -type d \( -name .git -o -name .venv \) -prune -o \
		-type d \( -name __pycache__ -o -name .mypy_cache \) \
		-prune -exec rm -rf {} +

.PHONY: clean install build run debug lint lint-strict
