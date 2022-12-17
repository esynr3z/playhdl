.PHONY: shell format check-format test lint

PKG = playhdl

shell:
	poetry shell

format:
	usort format .
	black .

check-format:
	usort check .
	black --check .

test:
	pytest --cov=$(PKG) --no-cov-on-fail --cov-report term-missing

lint:
	flake8
