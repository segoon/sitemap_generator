install:
	poetry install

lint:
	poetry run flake8 generator

generate:
	poetry run generator

async_generate:
	poetry run generator_async
