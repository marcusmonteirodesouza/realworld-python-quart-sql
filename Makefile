format:
	poetry run black .

run:
	poetry run dotenv run -- python -m conduit