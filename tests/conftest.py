import json
import random
import subprocess
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from .users import User, UserUser


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    subprocess.run(["make", "db-up"])


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

    data = {
        "user": {
            "email": faker.email(),
            "password": faker.password(),
            "username": faker.user_name(),
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 201

    response_data = await response.json

    created_user = response_data["user"]

    yield User(
        UserUser(
            email=created_user["email"],
            username=created_user["username"],
            token=created_user["token"],
            bio=created_user["bio"],
            image=created_user["image"],
        )
    )
