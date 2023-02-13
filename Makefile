pre-commit:
	poetry run pre-commit install

format:
	poetry run black .

db-up:
	docker compose up flyway --detach --wait

up:
	docker compose up -d --wait

up-build:
	docker compose up -d --wait --build

down:
	docker compose down

run:
	poetry run dotenv run -- python -m conduit

down-run:
	make down && make db-up && make run

test:
	make db-up && poetry run pytest

api-test:
	poetry run python api_test.py
