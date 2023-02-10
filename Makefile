format:
	poetry run black .

run:
	poetry run dotenv run -- python -m conduit

api-test:
	poetry run python api_test.py