install:
	uv sync

run:
	python3 application.py config.txt

debug:
	python3 -m pdb application.py config.txt

lint:
	flake8 . and mypy . \
		--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . and mypy . --strict

clean:
	rm -rf __pycache__ .mypy_cache
	rm -rf */__pycache__ */.mypy_cache
.PHONY: clean install run debug lint lint-strict
