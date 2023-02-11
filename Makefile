format:
	poetry run black .

db-up:
	docker-compose up flyway --detach --wait

db-down:
	docker-compose down flyway

run:
	poetry run dotenv run -- python -m conduit

test:
	poetry run pytest

api-test:
	poetry run python api_test.py