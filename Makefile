format:
	poetry run black .

run:
	poetry run dotenv run -- python -m conduit

up:
	docker-compose up --detach --wait

api-test:
	poetry run python api_test.py