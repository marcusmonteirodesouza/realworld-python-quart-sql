import pytest
import datetime
import json
import re
import secrets
import uuid
from ..utils import create_jwt


@pytest.mark.asyncio
async def test_should_return_201(app, faker, create_user):
    client = app.test_client()

    author = await create_user()

    data = {
        "article": {
            "title": "How to train your dragon",
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": ["training", "dragons", " some spaces "],
        }
    }

    response = await client.post(
        "/articles",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 201

    response_data = await response.json

    article = response_data["article"]

    now = datetime.datetime.now(tz=datetime.timezone.utc)

    assert re.match(r"how-to-train-your-dragon-\d+", article["slug"])
    assert article["title"] == data["article"]["title"]
    assert article["description"] == data["article"]["description"]
    assert article["description"] == data["article"]["description"]
    assert article["tagList"] == ["dragons", "some-spaces", "training"]
    created_at = datetime.datetime.fromisoformat(article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(article["updatedAt"])
    assert created_at == updated_at
    assert (now - created_at).total_seconds() < 1
    assert not article["favorited"]
    assert article["favoritesCount"] == 0
    assert article["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, faker, create_user
):
    client = app.test_client()

    author = await create_user()

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(),
        }
    }

    response = await client.post(
        "/articles",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {author.token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app, faker, create_user
):
    client = app.test_client()

    author = await create_user()

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(),
        }
    }

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=author.username, secret_key=secret_key)

    response = await client.post(
        "/articles",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_is_expired_should_return_401(app, faker, create_user):
    client = app.test_client()

    author = await create_user()

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(),
        }
    }

    token = create_jwt(username=author.username, expires_seconds=-1)

    response = await client.post(
        "/articles",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_author_is_not_found_should_return_401(app, faker):
    client = app.test_client()

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(),
        }
    }

    token = create_jwt(username=str(uuid.uuid4()))

    response = await client.post(
        "/articles",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
