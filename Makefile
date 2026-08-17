.PHONY: install run test lint check

install:
	uv sync

run:
	uv run adk web

test:
	uv run pytest

lint:
	uv run ruff check .

check: lint test

