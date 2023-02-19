import pytest
import datetime
import secrets
import uuid
from ..utils import create_jwt


def make_favorite_article_url(slug: str) -> str:
    return f"/articles/{slug}/favorite"


@pytest.mark.asyncio
async def test_when_author_is_followed_should_return_200(
    app, faker, create_user, follow_user, create_article
):
    client = app.test_client()

    user1 = await create_user()

    author = await create_user()

    await follow_user(follower_token=user1.token, username=author.username)

    created_article = await create_article(author_token=author.token)

    response1 = await client.post(
        make_favorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response1.status_code == 200

    response1_data = await response1.json

    response1_article = response1_data["article"]

    assert response1_article["slug"] == created_article.slug
    assert response1_article["title"] == created_article.title
    assert response1_article["description"] == created_article.description
    assert response1_article["body"] == created_article.body
    assert response1_article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(response1_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(response1_article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert response1_article["favorited"]
    assert response1_article["favoritesCount"] == 1
    assert response1_article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": True,
    }

    user2 = await create_user()

    await follow_user(follower_token=user2.token, username=author.username)

    response2 = await client.post(
        make_favorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user2.token}",
        },
    )

    assert response2.status_code == 200

    response2_data = await response2.json

    response2_article = response2_data["article"]

    assert response2_article["slug"] == created_article.slug
    assert response2_article["title"] == created_article.title
    assert response2_article["description"] == created_article.description
    assert response2_article["body"] == created_article.body
    assert response2_article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(response2_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(response2_article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert response2_article["favorited"]
    assert response2_article["favoritesCount"] == 2
    assert response2_article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_author_is_not_followed_should_return_200(
    app, faker, create_user, create_article
):
    client = app.test_client()

    user1 = await create_user()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    response1 = await client.post(
        make_favorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response1.status_code == 200

    response1_data = await response1.json

    response1_article = response1_data["article"]

    assert response1_article["slug"] == created_article.slug
    assert response1_article["title"] == created_article.title
    assert response1_article["description"] == created_article.description
    assert response1_article["body"] == created_article.body
    assert response1_article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(response1_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(response1_article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert response1_article["favorited"]
    assert response1_article["favoritesCount"] == 1
    assert response1_article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": False,
    }

    user2 = await create_user()

    response2 = await client.post(
        make_favorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user2.token}",
        },
    )

    assert response2.status_code == 200

    response2_data = await response2.json

    response2_article = response2_data["article"]

    assert response2_article["slug"] == created_article.slug
    assert response2_article["title"] == created_article.title
    assert response2_article["description"] == created_article.description
    assert response2_article["body"] == created_article.body
    assert response2_article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(response2_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(response2_article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert response2_article["favorited"]
    assert response2_article["favoritesCount"] == 2
    assert response2_article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_article_is_not_found_should_return_404(app, faker, create_user):
    client = app.test_client()

    user = await create_user()

    slug = str(uuid.uuid4())

    response = await client.post(
        make_favorite_article_url(slug=slug),
        headers={
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 404

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"slug {slug} not found"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, faker, create_user, create_article
):
    client = app.test_client()

    user = await create_user()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    response = await client.post(
        make_favorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Bearer {user.token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app, faker, create_user, create_article
):
    client = app.test_client()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=author.username, secret_key=secret_key)

    response = await client.post(
        make_favorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_is_expired_should_return_401(
    app, faker, create_user, create_article
):
    client = app.test_client()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    token = create_jwt(username=author.username, expires_seconds=-1)

    response = await client.post(
        make_favorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_user_is_not_found_should_return_401(
    app, faker, create_user, create_article
):
    client = app.test_client()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    token = create_jwt(username=str(uuid.uuid4()))

    response = await client.post(
        make_favorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
