import json
import random
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from .users import User


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest_asyncio.fixture(name="app", scope="function")
async def _app():
    from conduit import app

    async with app.test_app() as test_app:
        yield test_app


@pytest.fixture(scope="function", autouse=True)
def faker_seed():
    return random.random()


@pytest_asyncio.fixture(scope="function")
async def user(app, faker):
    client = app.test_client()

    register_user_data = {
        "user": {
            "email": faker.email(),
            "password": faker.password(),
            "username": faker.user_name(),
        }
    }

    register_user_response = await client.post(
        "/users",
        data=json.dumps(register_user_data),
        headers={"Content-Type": "application/json"},
    )

    assert register_user_response.status_code == 201

    register_user_response_data = await register_user_response.json

    created_user = register_user_response_data["user"]

    update_user_data = {
        "user": {
            "bio": faker.paragraph(),
            "image": faker.url(),
        }
    }

    update_user_response = await client.put(
        "/user",
        data=json.dumps(update_user_data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {created_user['token']}",
        },
    )

    assert update_user_response.status_code == 200

    update_user_response_data = await update_user_response.json

    updated_user_user = update_user_response_data["user"]

    yield User(
        email=created_user["email"],
        username=created_user["username"],
        token=created_user["token"],
        bio=updated_user_user["bio"],
        image=updated_user_user["image"],
        password=register_user_data["user"]["password"],
    )
