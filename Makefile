pre-commit:
	poetry run pre-commit install

format:
	poetry run black .

db-up:
	docker compose up flyway --detach --wait

up:
	docker compose up -d --wait

down:
	docker compose down

run:
	poetry run dotenv run -- python -m conduit

test:
	make db-up && poetry run pytest

api-test:
	poetry run python api_test.py
