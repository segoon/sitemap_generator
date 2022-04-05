install:
	poetry install

lint:
	poetry run flake8 generator

generate:
	poetry run generator
