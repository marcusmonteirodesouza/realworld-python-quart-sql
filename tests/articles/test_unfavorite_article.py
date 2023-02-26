import pytest
import datetime
import secrets
import uuid
from ..utils import create_jwt


def make_unfavorite_article_url(slug: str) -> str:
    return f"/api/articles/{slug}/favorite"


@pytest.mark.asyncio
async def test_when_author_is_followed_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    get_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()

    author = await create_user_and_decode()

    created_article = await create_article_and_decode(author_token=author.token)

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    await favorite_article_and_decode(user_token=user1.token, slug=created_article.slug)

    response = await client.delete(
        make_unfavorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    response_article = response_data["article"]

    assert response_article["slug"] == created_article.slug
    assert response_article["title"] == created_article.title
    assert response_article["description"] == created_article.description
    assert response_article["body"] == created_article.body
    assert response_article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(response_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(response_article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert not response_article["favorited"]
    assert response_article["favoritesCount"] == 0
    assert response_article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": True,
    }

    got_article = await get_article_and_decode(slug=response_article["slug"])

    assert not got_article.favorited


@pytest.mark.asyncio
async def test_when_author_is_not_followed_should_return_200(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
    get_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()

    author = await create_user_and_decode()

    created_article = await create_article_and_decode(author_token=author.token)

    await favorite_article_and_decode(user_token=user1.token, slug=created_article.slug)

    response = await client.delete(
        make_unfavorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    response_article = response_data["article"]

    assert response_article["slug"] == created_article.slug
    assert response_article["title"] == created_article.title
    assert response_article["description"] == created_article.description
    assert response_article["body"] == created_article.body
    assert response_article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(response_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(response_article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert not response_article["favorited"]
    assert response_article["favoritesCount"] == 0
    assert response_article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": False,
    }

    got_article = await get_article_and_decode(slug=response_article["slug"])

    assert not got_article.favorited


@pytest.mark.asyncio
async def test_when_article_is_already_not_favorited_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    get_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()

    author = await create_user_and_decode()

    created_article = await create_article_and_decode(author_token=author.token)

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    response = await client.delete(
        make_unfavorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    response_article = response_data["article"]

    assert response_article["slug"] == created_article.slug
    assert response_article["title"] == created_article.title
    assert response_article["description"] == created_article.description
    assert response_article["body"] == created_article.body
    assert response_article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(response_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(response_article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert not response_article["favorited"]
    assert response_article["favoritesCount"] == 0
    assert response_article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": True,
    }

    got_article = await get_article_and_decode(slug=response_article["slug"])

    assert not got_article.favorited


@pytest.mark.asyncio
async def test_when_article_is_not_found_should_return_404(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    slug = str(uuid.uuid4())

    response = await client.delete(
        make_unfavorite_article_url(slug=slug),
        headers={
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

    created_article = await create_article_and_decode(author_token=author.token)

    response = await client.delete(
        make_unfavorite_article_url(slug=created_article.slug),
        headers={
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

    created_article = await create_article_and_decode(author_token=author.token)

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=author.username, secret_key=secret_key)

    response = await client.delete(
        make_unfavorite_article_url(slug=created_article.slug),
        headers={
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

    created_article = await create_article_and_decode(author_token=author.token)

    token = create_jwt(username=author.username, expires_seconds=-1)

    response = await client.delete(
        make_unfavorite_article_url(slug=created_article.slug),
        headers={
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

    response = await client.delete(
        make_unfavorite_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
