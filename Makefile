.DEFAULT_GOAL := default

.PHONY: test
test:
	poetry run pytest --cov=yuisub --cov-report=xml --cov-report=html

.PHONY: lint
lint:
	poetry run pre-commit install
	poetry run pre-commit run --all-files

.PHONY: build
build:
	poetry build
