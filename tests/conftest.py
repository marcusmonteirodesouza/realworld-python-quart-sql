import datetime
import json
import random
import uuid
from typing import List, Optional

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from .articles.comment import Comment, CommentAuthorProfile
from .profiles import Profile
from .users import User
from .articles import Article, ArticleAuthorProfile


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
async def create_user_and_decode(app, faker):
    async def _create_user_and_decode() -> User:
        client = app.test_client()

        register_user_data = {
            "user": {
                "email": f"{str(uuid.uuid4())}@test.com",
                "password": faker.password(),
                "username": str(uuid.uuid4()),
            }
        }

        register_user_response = await client.post(
            "/api/users",
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
            "/api/user",
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

    yield _create_user_and_decode


@pytest_asyncio.fixture(scope="function")
async def follow_user_and_decode(app):
    async def _follow_user_and_decode(follower_token: str, username: str) -> Profile:
        client = app.test_client()

        response = await client.post(
            f"/api/profiles/{username}/follow",
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

    yield _follow_user_and_decode


@pytest_asyncio.fixture(scope="function")
async def unfollow_user_and_decode(app):
    async def _unfollow_user_and_decode(follower_token: str, username: str) -> Profile:
        client = app.test_client()

        response = await client.delete(
            f"/api/profiles/{username}/follow",
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

    yield _unfollow_user_and_decode


@pytest_asyncio.fixture(scope="function")
async def get_profile_and_decode(app):
    async def _get_profile_and_decode(
        username: str, follower_token: Optional[str]
    ) -> Profile:
        client = app.test_client()

        headers = {}

        if follower_token:
            headers["Authorization"] = f"Token {follower_token}"

        response = await client.get(
            f"/api/profiles/{username}",
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

    yield _get_profile_and_decode


@pytest_asyncio.fixture(scope="function")
async def create_article_and_decode(app, faker):
    async def _create_article_and_decode(
        author_token: str, tags: Optional[List[str]] = None
    ) -> Article:
        client = app.test_client()

        data = {
            "article": {
                "title": faker.sentence(),
                "description": faker.sentence(),
                "body": faker.paragraph(),
                "tagList": tags if tags else faker.words(nb=10, unique=True),
            }
        }

        response = await client.post(
            "/api/articles",
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
            author=ArticleAuthorProfile(
                username=author_data["username"],
                bio=author_data["bio"],
                image=author_data["image"],
                following=author_data["following"],
            ),
        )

    yield _create_article_and_decode


@pytest_asyncio.fixture(scope="function")
async def get_article(app):
    async def _get_article(slug: str, user_token: Optional[str] = None) -> Article:
        client = app.test_client()

        headers = {}

        if user_token:
            headers["Authorization"] = f"Token {user_token}"

        response = await client.get(
            f"/api/articles/{slug}",
            headers=headers,
        )

        return response

    yield _get_article


@pytest_asyncio.fixture(scope="function")
async def get_article_and_decode(get_article):
    async def _get_article_and_decode(
        slug: str, user_token: Optional[str] = None
    ) -> Article:
        response = await get_article(slug=slug, user_token=user_token)

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
            author=ArticleAuthorProfile(
                username=author_data["username"],
                bio=author_data["bio"],
                image=author_data["image"],
                following=author_data["following"],
            ),
        )

    yield _get_article_and_decode


@pytest_asyncio.fixture(scope="function")
async def favorite_article_and_decode(app):
    async def _favorite_article_and_decode(user_token: str, slug: str) -> Article:
        client = app.test_client()

        response = await client.post(
            f"/api/articles/{slug}/favorite",
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
            author=ArticleAuthorProfile(
                username=author_data["username"],
                bio=author_data["bio"],
                image=author_data["image"],
                following=author_data["following"],
            ),
        )

    yield _favorite_article_and_decode


@pytest_asyncio.fixture(scope="function")
async def add_comment_to_article_and_decode(app, faker):
    async def _add_comment_to_article_and_decode(
        author_token: str, slug: str
    ) -> Comment:
        client = app.test_client()

        data = {"comment": {"body": faker.paragraph()}}

        response = await client.post(
            f"/api/articles/{slug}/comments",
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {author_token}",
            },
        )

        assert response.status_code == 201

        response_data = await response.json

        comment_data = response_data["comment"]

        author_data = comment_data["author"]

        return Comment(
            id=comment_data["id"],
            body=comment_data["body"],
            created_at=datetime.datetime.fromisoformat(comment_data["createdAt"]),
            updated_at=datetime.datetime.fromisoformat(comment_data["updatedAt"]),
            author=CommentAuthorProfile(
                username=author_data["username"],
                bio=author_data["bio"],
                image=author_data["image"],
                following=author_data["following"],
            ),
        )

    yield _add_comment_to_article_and_decode


@pytest_asyncio.fixture(scope="function")
async def list_comments_from_article_and_decode(app):
    async def _list_comments_from_article_and_decode(
        slug: str, user_token: Optional[str]
    ) -> List[Comment]:
        client = app.test_client()

        headers = {}

        if user_token:
            headers["Authorization"] = (f"Token {user_token}",)

        response = await client.get(
            f"/api/articles/{slug}/comments",
            headers=headers,
        )

        assert response.status_code == 200

        response_data = await response.json

        comments_data = response_data["comments"]

        comments = []

        for comment_data in comments_data:
            author_data = comment_data["author"]

            comment = Comment(
                id=comment_data["id"],
                body=comment_data["body"],
                created_at=datetime.datetime.fromisoformat(comment_data["createdAt"]),
                updated_at=datetime.datetime.fromisoformat(comment_data["updatedAt"]),
                author=CommentAuthorProfile(
                    username=author_data["username"],
                    bio=author_data["bio"],
                    image=author_data["image"],
                    following=author_data["following"],
                ),
            )

            comments.append(comment)

        return comments

    yield _list_comments_from_article_and_decode
