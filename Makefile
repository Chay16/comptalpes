#!make
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euc
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

.PHONY: install lint format test cov cov-html webapp server app

install:
	@uv lock --check
	@uv sync
	@uv run pre-commit install

lint:
	@uv run ruff check .
	@uv run ruff format --check .

format:
	@uv run ruff format .
	@uv run ruff check --fix .

test: install
	@uv run pytest -vvv -s

cov: install
	@uv run pytest --cov src --cov-branch

cov-html: install
	@uv run pytest --cov src --cov-branch --cov-report html --cov-report term

webapp:
	@uv run streamlit run src/webapp/app.py

server:
	@uv run fastapi dev src/api/main.py

app:
	@mkdir -p logs
	@uv run fastapi dev src/api/main.py >logs/api.log 2>&1 & \
	api_pid=$$!; \
	trap 'kill $$api_pid 2>/dev/null' EXIT INT TERM; \
	until curl -sf -o /dev/null http://127.0.0.1:8000/docs; do sleep 0.5; done; \
	echo "API up (log: logs/api.log)"; \
	uv run streamlit run src/webapp/app.py
