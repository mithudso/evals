.PHONY: setup test lint format-check docs-index docs-check check build audit

setup:
	uv sync --extra dev --frozen

test:
	uv run --extra dev --frozen pytest

lint:
	uv run --extra dev --frozen ruff check runner benchmarks scripts tests

format-check:
	uv run --extra dev --frozen ruff format --check runner benchmarks scripts tests

docs-index:
	uv run --extra dev --frozen python scripts/generate_doc_indexes.py

docs-check:
	uv run --extra dev --frozen python scripts/check_doc_indexes.py

check: lint format-check test docs-check

build:
	uv build

audit:
	uv run --extra dev --frozen pip-audit --skip-editable
