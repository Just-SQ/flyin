# Makefile for the Fly-in drone-routing project.
# Uses uv for dependency management and command execution.

.PHONY: install run debug clean lint lint-strict

# Install project dependencies (matplotlib, pydantic) into the uv venv.
install:
	uv sync

# Run the simulation.
run:
	uv run python mainV2.py

# Run the simulation under Python's built-in debugger (pdb).
debug:
	uv run python -m pdb mainV2.py

# Remove Python caches and build artifacts.
clean:
	rm -rf .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +

# Style + type checks required by the subject.
lint:
	uv run --with flake8 flake8 .
	uv run --with mypy mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# Optional stricter type checking.
lint-strict:
	uv run --with flake8 flake8 .
	uv run --with mypy mypy . --strict
