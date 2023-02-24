import pytest
import datetime
import json
import secrets
import uuid
from ..utils import create_jwt


def make_add_comment_to_article_url(slug: str) -> str:
    return f"/articles/{slug}/comments"


@pytest.mark.asyncio
async def test_when_author_is_followed_should_return_201(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
):
    client = app.test_client()

    user = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    data = {"comment": {"body": faker.paragraph()}}

    response = await client.post(
        make_add_comment_to_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 201

    response_data = await response.json

    response_comment = response_data["comment"]

    now = datetime.datetime.now(tz=datetime.timezone.utc)

    uuid.UUID(response_comment["id"])
    assert response_comment["body"] == data["comment"]["body"]
    created_at = datetime.datetime.fromisoformat(response_comment["createdAt"])
    updated_at = datetime.datetime.fromisoformat(response_comment["updatedAt"])
    assert created_at == updated_at
    assert (now - created_at).total_seconds() < 1
    assert response_comment["author"] == {
        "username": user.username,
        "bio": user.bio,
        "image": user.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_article_is_not_found_should_return_404(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    slug = str(uuid.uuid4())

    data = {"comment": {"body": faker.paragraph()}}

    response = await client.post(
        make_add_comment_to_article_url(slug=slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 404

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"slug {slug} not found"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, faker, create_user_and_decode, create_article_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    data = {"comment": {"body": faker.paragraph()}}

    response = await client.post(
        make_add_comment_to_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user.token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app, faker, create_user_and_decode, create_article_and_decode
):
    client = app.test_client()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=author.username, secret_key=secret_key)

    data = {"comment": {"body": faker.paragraph()}}

    response = await client.post(
        make_add_comment_to_article_url(slug=article.slug),
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
async def test_when_token_is_expired_should_return_401(
    app, faker, create_user_and_decode, create_article_and_decode
):
    client = app.test_client()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    token = create_jwt(username=author.username, expires_seconds=-1)

    data = {"comment": {"body": faker.paragraph()}}

    response = await client.post(
        make_add_comment_to_article_url(slug=article.slug),
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
async def test_when_user_is_not_found_should_return_401(
    app, faker, create_user_and_decode, create_article_and_decode
):
    client = app.test_client()

    author = await create_user_and_decode()

    created_article = await create_article_and_decode(author_token=author.token)

    token = create_jwt(username=str(uuid.uuid4()))

    data = {"comment": {"body": faker.paragraph()}}

    response = await client.post(
        make_add_comment_to_article_url(slug=created_article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
