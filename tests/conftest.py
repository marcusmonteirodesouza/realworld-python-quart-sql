import datetime
import json
import random
import uuid
from typing import Optional

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from .profiles import Profile
from .users import User
from .articles import Article, AuthorProfile


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
async def create_user(app, faker):
    async def _create_user() -> User:
        client = app.test_client()

        register_user_data = {
            "user": {
                "email": f"{str(uuid.uuid4())}@test.com",
                "password": faker.password(),
                "username": str(uuid.uuid4()),
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

        return User(
            email=created_user["email"],
            username=created_user["username"],
            token=created_user["token"],
            bio=updated_user_user["bio"],
            image=updated_user_user["image"],
            password=register_user_data["user"]["password"],
        )

    yield _create_user


@pytest_asyncio.fixture(scope="function")
async def follow_user(app):
    async def _follow_user(follower_token: str, username: str) -> Profile:
        client = app.test_client()

        response = await client.post(
            f"/profiles/{username}/follow",
            headers={"Authorization": f"Token {follower_token}"},
        )

        assert response.status_code == 200

        response_data = await response.json

        profile_data = response_data["profile"]

        return Profile(
            username=profile_data["username"],
            bio=profile_data["bio"],
            image=profile_data["image"],
            following=profile_data["following"],
        )

    yield _follow_user


@pytest_asyncio.fixture(scope="function")
async def unfollow_user(app):
    async def _unfollow_user(follower_token: str, username: str) -> Profile:
        client = app.test_client()

        response = await client.delete(
            f"/profiles/{username}/follow",
            headers={"Authorization": f"Token {follower_token}"},
        )

        assert response.status_code == 200

        response_data = await response.json

        profile_data = response_data["profile"]

        return Profile(
            username=profile_data["username"],
            bio=profile_data["bio"],
            image=profile_data["image"],
            following=profile_data["following"],
        )

    yield _unfollow_user


@pytest_asyncio.fixture(scope="function")
async def get_profile(app):
    async def _get_profile(username: str, follower_token: Optional[str]) -> Profile:
        client = app.test_client()

        headers = {}

        if follower_token:
            headers["Authorization"] = f"Token {follower_token}"

        response = await client.get(
            f"/profiles/{username}",
            headers=headers,
        )

        assert response.status_code == 200

        response_data = await response.json

        profile_data = response_data["profile"]

        return Profile(
            username=profile_data["username"],
            bio=profile_data["bio"],
            image=profile_data["image"],
            following=profile_data["following"],
        )

    yield _get_profile


@pytest_asyncio.fixture(scope="function")
async def create_article(app, faker):
    async def _create_article(author_token: str) -> Article:
        client = app.test_client()

        data = {
            "article": {
                "title": faker.sentence(),
                "description": faker.sentence(),
                "body": faker.paragraph(),
                "tagList": faker.words(nb=10, unique=True),
            }
        }

        response = await client.post(
            "/articles",
            data=json.dumps(data),
            headers={
                "Authorization": f"Token {author_token}",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 201

        response_data = await response.json

        article_data = response_data["article"]

        author_data = article_data["author"]

        return Article(
            slug=article_data["slug"],
            title=article_data["title"],
            description=article_data["description"],
            body=article_data["body"],
            tag_list=article_data["tagList"],
            created_at=datetime.datetime.fromisoformat(article_data["createdAt"]),
            updated_at=datetime.datetime.fromisoformat(article_data["updatedAt"]),
            favorited=article_data["favorited"],
            favorites_count=article_data["favoritesCount"],
            author=AuthorProfile(
                username=author_data["username"],
                bio=author_data["bio"],
                image=author_data["image"],
                following=author_data["following"],
            ),
        )

    yield _create_article


@pytest_asyncio.fixture(scope="function")
async def get_article(app, faker):
    async def _get_article(slug: str, user_token: Optional[str] = None) -> Article:
        client = app.test_client()

        headers = {}

        if user_token:
            headers["Authorization"] = f"Token {user_token}"

        response = await client.get(
            f"/articles/{slug}",
            headers=headers,
        )

        assert response.status_code == 200

        response_data = await response.json

        article_data = response_data["article"]

        author_data = article_data["author"]

        return Article(
            slug=article_data["slug"],
            title=article_data["title"],
            description=article_data["description"],
            body=article_data["body"],
            tag_list=article_data["tagList"],
            created_at=datetime.datetime.fromisoformat(article_data["createdAt"]),
            updated_at=datetime.datetime.fromisoformat(article_data["updatedAt"]),
            favorited=article_data["favorited"],
            favorites_count=article_data["favoritesCount"],
            author=AuthorProfile(
                username=author_data["username"],
                bio=author_data["bio"],
                image=author_data["image"],
                following=author_data["following"],
            ),
        )

    yield _get_article


@pytest_asyncio.fixture(scope="function")
async def favorite_article(app, faker):
    async def _favorite_article(user_token: str, article_slug: str) -> Article:
        client = app.test_client()

        response = await client.post(
            f"/articles/{article_slug}/favorite",
            headers={
                "Authorization": f"Token {user_token}",
            },
        )

        assert response.status_code == 200

        response_data = await response.json

        article_data = response_data["article"]

        author_data = article_data["author"]

        return Article(
            slug=article_data["slug"],
            title=article_data["title"],
            description=article_data["description"],
            body=article_data["body"],
            tag_list=article_data["tagList"],
            created_at=datetime.datetime.fromisoformat(article_data["createdAt"]),
            updated_at=datetime.datetime.fromisoformat(article_data["updatedAt"]),
            favorited=article_data["favorited"],
            favorites_count=article_data["favoritesCount"],
            author=AuthorProfile(
                username=author_data["username"],
                bio=author_data["bio"],
                image=author_data["image"],
                following=author_data["following"],
            ),
        )

    yield _favorite_article
