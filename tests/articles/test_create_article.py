import pytest
import datetime
import json
import re
import secrets
import uuid
import validators
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
            "tagList": [
                "training",
                "dragons",
                " some spaces ",
                "repeated",
                "repeated",
                "123",
            ],
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

    assert re.match(r"how-to-train-your-dragon-\S+", article["slug"])
    assert article["title"] == data["article"]["title"]
    assert article["description"] == data["article"]["description"]
    assert article["body"] == data["article"]["body"]
    assert article["tagList"] == [
        "123",
        "dragons",
        "repeated",
        "some-spaces",
        "training",
    ]
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
async def test_when_creating_article_with_same_title_as_an_existing_one_should_return_201(
    app, faker, create_user, create_article, get_article
):
    client = app.test_client()

    author1 = await create_user()

    author2 = await create_user()

    existing_article = await create_article(author_token=author2.token)

    data = {
        "article": {
            "title": existing_article.title,
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10),
        }
    }

    response = await client.post(
        "/articles",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author1.token}",
        },
    )

    assert response.status_code == 201

    response_data = await response.json

    article = response_data["article"]

    assert article["title"] == existing_article.title

    got_existing_article = await get_article(slug=existing_article.slug)

    assert got_existing_article.slug == existing_article.slug
    assert article["slug"] != got_existing_article.slug


@pytest.mark.asyncio
async def test_when_tagList_is_not_sent_should_return_201(app, faker, create_user):
    client = app.test_client()

    author = await create_user()

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
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

    assert validators.slug(article["slug"])
    assert article["title"] == data["article"]["title"]
    assert article["description"] == data["article"]["description"]
    assert article["body"] == data["article"]["body"]
    assert article["tagList"] == []
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
async def test_when_article_is_not_sent_should_return_400(app, faker, create_user):
    client = app.test_client()

    author = await create_user()

    data = {}

    response = await client.post(
        "/articles",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "The browser (or proxy) sent a request that this server could not understand."
    )


@pytest.mark.asyncio
async def test_when_title_is_not_sent_should_return_400(app, faker, create_user):
    client = app.test_client()

    author = await create_user()

    data = {
        "article": {
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10, unique=True),
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

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "The browser (or proxy) sent a request that this server could not understand."
    )


@pytest.mark.asyncio
async def test_when_description_is_not_sent_should_return_400(app, faker, create_user):
    client = app.test_client()

    author = await create_user()

    data = {
        "article": {
            "title": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10, unique=True),
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

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "The browser (or proxy) sent a request that this server could not understand."
    )


@pytest.mark.asyncio
async def test_when_body_is_not_sent_should_return_400(app, faker, create_user):
    client = app.test_client()

    author = await create_user()

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.paragraph(),
            "tagList": faker.words(nb=10, unique=True),
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

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "The browser (or proxy) sent a request that this server could not understand."
    )


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
            "tagList": faker.words(nb=10, unique=True),
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
            "tagList": faker.words(nb=10, unique=True),
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
            "tagList": faker.words(nb=10, unique=True),
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
            "tagList": faker.words(nb=10, unique=True),
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
