import subprocess
import pytest
import pytest_asyncio
import random
from dotenv import load_dotenv


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


@pytest_asyncio.fixture(scope="function")
async def app():
    from conduit import app

    async with app.test_app() as test_app:
        yield test_app


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return random.random()
