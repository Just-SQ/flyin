
.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run python main.py

debug:
	uv run python -m pdb main.py

clean:
	rm -rf .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +

lint:
	uv run flake8 . --exclude .venv
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
