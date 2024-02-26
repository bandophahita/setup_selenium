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

black-fix:
	black .

ruff-check:
	ruff check .

ruff-fix:
	ruff check . --fix --show-fixes

mypy:
	mypy .

.PHONY: black-check black-fix ruff-check ruff-fix mypy

pre-check-in: black-check ruff-check mypy

pre-check-in-fix: black-fix ruff-fix mypy

.PHONY: pre-check-in pre-check-in-fix

test:
	python3 -m pytest tests

.PHONY: test 
