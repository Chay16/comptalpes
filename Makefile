#!make
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euc
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

.PHONY: install lint format test cov cov-html

install:
	@uv lock --check
	@uv sync

lint:
	@uv run ruff check .

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
	@uv run streamlit run src/webapp/home.py

server:
	@uv run fastapi dev src/api/main.py
