requirements:
	poetry export --without-hashes --extras dev -f requirements.txt > requirements.txt

sync:
	poetry install --extras dev --sync

update_lock_only:
	poetry update --lock

update: update_lock_only
	poetry install --extras dev

.PHONY: requirements sync update update_lock_only

black-check:
	black --check .

black:
	black .

isort-check:
	isort . --check

isort:
	isort .

ruff:
	ruff check .

ruff-fix:
	ruff check . --fix --show-fixes

mypy:
	mypy .

lint: isort-check ruff mypy

test:
	python3 -m pytest tests

.PHONY: black-check black isort-check isort ruff ruff-fix mypy lint test 

pre-check-in: black-check lint

pre-check-in-fix: black isort ruff-fix mypy

.PHONY: pre-check-in pre-check-in-fix
