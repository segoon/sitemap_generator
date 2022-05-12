install:
	poetry install

lint:
	poetry run flake8 generator

generate:
	poetry run generator $(URL)

generate_async:
	poetry run generator_async $(URL)
