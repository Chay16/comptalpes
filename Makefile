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
	@uv run ruff check --fix .
	@uv run ruff format .

test: install
	@uv run pytest

cov: install
	@uv run pytest --cov src --cov-branch

cov-html: install
	@uv run pytest --cov src --cov-branch --cov-report html --cov-report term
