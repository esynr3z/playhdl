.PHONY: setup-dev format check-format test lint type pre-commit

PKG = playhdl
PYTHON_VERSION ?= 3.8

POETRY_RUN = poetry run

setup-dev:
	poetry env use $(PYTHON_VERSION)
	poetry install

format:
	$(POETRY_RUN) usort format .
	$(POETRY_RUN) black .

check-format:
	$(POETRY_RUN) usort check .
	$(POETRY_RUN) black --check .

test:
	$(POETRY_RUN) pytest --cov=$(PKG) --no-cov-on-fail --cov-report term-missing $(ARGS)

lint:
	$(POETRY_RUN) flake8

type:
	$(POETRY_RUN) mypy -p $(PKG)
	$(POETRY_RUN) mypy -p tests

pre-commit: check-format lint type test
