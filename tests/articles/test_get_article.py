import pytest
import datetime
import secrets
import uuid
from ..utils import create_jwt


def make_get_article_url(slug: str) -> str:
    return f"/articles/{slug}"


@pytest.mark.asyncio
async def test_when_token_is_sent_and_article_is_favorited_and_author_is_followed_should_return_200(
    app, faker, create_user, follow_user, create_article, favorite_article
):
    client = app.test_client()

    user1 = await create_user()

    user2 = await create_user()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    await follow_user(follower_token=user1.token, username=author.username)

    await favorite_article(user_token=user1.token, article_slug=created_article.slug)

    await favorite_article(user_token=user2.token, article_slug=created_article.slug)

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    article = response_data["article"]

    assert article["slug"] == created_article.slug
    assert article["title"] == created_article.title
    assert article["description"] == created_article.description
    assert article["body"] == created_article.body
    assert article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert article["favorited"]
    assert article["favoritesCount"] == 2
    assert article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_token_is_sent_and_article_is_not_favorited_and_author_is_followed_should_return_200(
    app, faker, create_user, follow_user, create_article, favorite_article
):
    client = app.test_client()

    user1 = await create_user()

    user2 = await create_user()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    await follow_user(follower_token=user1.token, username=author.username)

    await favorite_article(user_token=user2.token, article_slug=created_article.slug)

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    article = response_data["article"]

    assert article["slug"] == created_article.slug
    assert article["title"] == created_article.title
    assert article["description"] == created_article.description
    assert article["body"] == created_article.body
    assert article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert not article["favorited"]
    assert article["favoritesCount"] == 1
    assert article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_token_is_sent_and_article_is_favorited_and_author_is_not_followed_should_return_200(
    app, faker, create_user, create_article, favorite_article
):
    client = app.test_client()

    user1 = await create_user()

    user2 = await create_user()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    await favorite_article(user_token=user1.token, article_slug=created_article.slug)

    await favorite_article(user_token=user2.token, article_slug=created_article.slug)

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    article = response_data["article"]

    assert article["slug"] == created_article.slug
    assert article["title"] == created_article.title
    assert article["description"] == created_article.description
    assert article["body"] == created_article.body
    assert article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert article["favorited"]
    assert article["favoritesCount"] == 2
    assert article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_token_is_sent_and_article_is_not_favorited_and_author_is_not_followed_should_return_200(
    app, faker, create_user, follow_user, create_article, favorite_article
):
    client = app.test_client()

    user1 = await create_user()

    user2 = await create_user()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    await favorite_article(user_token=user2.token, article_slug=created_article.slug)

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    article = response_data["article"]

    assert article["slug"] == created_article.slug
    assert article["title"] == created_article.title
    assert article["description"] == created_article.description
    assert article["body"] == created_article.body
    assert article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert not article["favorited"]
    assert article["favoritesCount"] == 1
    assert article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_token_is_not_sent_should_return_200(
    app, faker, create_user, follow_user, create_article, favorite_article
):
    client = app.test_client()

    user = await create_user()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    await follow_user(follower_token=user.token, username=author.username)

    await favorite_article(user_token=user.token, article_slug=created_article.slug)

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
        headers={},
    )

    assert response.status_code == 200

    response_data = await response.json

    article = response_data["article"]

    assert article["slug"] == created_article.slug
    assert article["title"] == created_article.title
    assert article["description"] == created_article.description
    assert article["body"] == created_article.body
    assert article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert not article["favorited"]
    assert article["favoritesCount"] == 1
    assert article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_article_is_not_found_should_return_404(app, faker):
    client = app.test_client()

    slug = str(uuid.uuid4())

    response = await client.get(
        make_get_article_url(slug=slug),
        headers={},
    )

    assert response.status_code == 404

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"slug {slug} not found"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_200(
    app, faker, create_user, create_article
):
    client = app.test_client()

    user = await create_user()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Bearer {user.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    article = response_data["article"]

    assert article["slug"] == created_article.slug
    assert article["title"] == created_article.title
    assert article["description"] == created_article.description
    assert article["body"] == created_article.body
    assert article["tagList"] == created_article.tag_list
    created_at = datetime.datetime.fromisoformat(article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(article["updatedAt"])
    assert created_at == created_article.created_at
    assert updated_at == created_article.updated_at
    assert not article["favorited"]
    assert article["favoritesCount"] == 0
    assert article["author"] == {
        "username": created_article.author.username,
        "bio": created_article.author.bio,
        "image": created_article.author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app, faker, create_user, create_article
):
    client = app.test_client()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=author.username, secret_key=secret_key)

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
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

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
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

    response = await client.get(
        make_get_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
