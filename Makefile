.PHONY: format check-format test lint

PKG = playhdl
POETRY_RUN = poetry run

format:
	$(POETRY_RUN) usort format .
	$(POETRY_RUN) black .

check-format:
	$(POETRY_RUN) usort check .
	$(POETRY_RUN) black --check .

test:
	$(POETRY_RUN) pytest --cov=$(PKG) --no-cov-on-fail --cov-report term-missing

lint:
	$(POETRY_RUN) flake8
