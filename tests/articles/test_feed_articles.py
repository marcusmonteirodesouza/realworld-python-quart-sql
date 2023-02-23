import pytest
import datetime
import secrets
import urllib.parse
import uuid
from typing import Optional
from ..utils import create_jwt


def make_feed_articles_url(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    params = {}

    if limit:
        params["limit"] = limit

    if offset:
        params["offset"] = offset

    encoded_params = urllib.parse.urlencode(params)

    return f"/articles/feed?{encoded_params}"


@pytest.mark.asyncio
async def test_when_all_query_args_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user = await create_user_and_decode()

    author1 = await create_user_and_decode()
    author2 = await create_user_and_decode()
    author3 = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author1.token)
    article2 = await create_article_and_decode(author_token=author2.token)
    article3 = await create_article_and_decode(author_token=author3.token)
    article4 = await create_article_and_decode(author_token=author1.token)
    article5 = await create_article_and_decode(author_token=author2.token)
    article6 = await create_article_and_decode(author_token=author3.token)
    article7 = await create_article_and_decode(author_token=author1.token)
    article8 = await create_article_and_decode(author_token=author2.token)
    article9 = await create_article_and_decode(author_token=author3.token)

    await follow_user_and_decode(follower_token=user.token, username=author1.username)
    await follow_user_and_decode(follower_token=user.token, username=author2.username)

    await favorite_article_and_decode(user_token=user.token, slug=article5.slug)

    limit = 3
    offset = 1

    response = await client.get(
        make_feed_articles_url(
            limit=limit,
            offset=offset,
        ),
        headers={
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == limit
    assert articles_count == limit

    assert articles[0]["slug"] == article7.slug
    assert articles[0]["title"] == article7.title
    assert articles[0]["description"] == article7.description
    assert articles[0]["body"] == article7.body
    assert articles[0]["tagList"] == article7.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article7.created_at
    assert updated_at == article7.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 0
    assert articles[0]["author"] == {
        "username": author1.username,
        "bio": author1.bio,
        "image": author1.image,
        "following": True,
    }

    assert articles[1]["slug"] == article5.slug
    assert articles[1]["title"] == article5.title
    assert articles[1]["description"] == article5.description
    assert articles[1]["body"] == article5.body
    assert articles[1]["tagList"] == article5.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article5.created_at
    assert updated_at == article5.updated_at
    assert articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 1
    assert articles[1]["author"] == {
        "username": author2.username,
        "bio": author2.bio,
        "image": author2.image,
        "following": True,
    }

    assert articles[2]["slug"] == article4.slug
    assert articles[2]["title"] == article4.title
    assert articles[2]["description"] == article4.description
    assert articles[2]["body"] == article4.body
    assert articles[2]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 0
    assert articles[2]["author"] == {
        "username": author1.username,
        "bio": author1.bio,
        "image": author1.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_all_query_args_but_limit_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user = await create_user_and_decode()

    author1 = await create_user_and_decode()
    author2 = await create_user_and_decode()
    author3 = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author1.token)
    article2 = await create_article_and_decode(author_token=author2.token)
    article3 = await create_article_and_decode(author_token=author3.token)
    article4 = await create_article_and_decode(author_token=author1.token)
    article5 = await create_article_and_decode(author_token=author2.token)
    article6 = await create_article_and_decode(author_token=author3.token)
    article7 = await create_article_and_decode(author_token=author1.token)
    article8 = await create_article_and_decode(author_token=author2.token)
    article9 = await create_article_and_decode(author_token=author3.token)

    await follow_user_and_decode(follower_token=user.token, username=author1.username)
    await follow_user_and_decode(follower_token=user.token, username=author2.username)

    await favorite_article_and_decode(user_token=user.token, slug=article5.slug)

    offset = 1

    response = await client.get(
        make_feed_articles_url(
            offset=offset,
        ),
        headers={
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == 5
    assert articles_count == 5

    assert articles[0]["slug"] == article7.slug
    assert articles[0]["title"] == article7.title
    assert articles[0]["description"] == article7.description
    assert articles[0]["body"] == article7.body
    assert articles[0]["tagList"] == article7.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article7.created_at
    assert updated_at == article7.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 0
    assert articles[0]["author"] == {
        "username": author1.username,
        "bio": author1.bio,
        "image": author1.image,
        "following": True,
    }

    assert articles[1]["slug"] == article5.slug
    assert articles[1]["title"] == article5.title
    assert articles[1]["description"] == article5.description
    assert articles[1]["body"] == article5.body
    assert articles[1]["tagList"] == article5.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article5.created_at
    assert updated_at == article5.updated_at
    assert articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 1
    assert articles[1]["author"] == {
        "username": author2.username,
        "bio": author2.bio,
        "image": author2.image,
        "following": True,
    }

    assert articles[2]["slug"] == article4.slug
    assert articles[2]["title"] == article4.title
    assert articles[2]["description"] == article4.description
    assert articles[2]["body"] == article4.body
    assert articles[2]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 0
    assert articles[2]["author"] == {
        "username": author1.username,
        "bio": author1.bio,
        "image": author1.image,
        "following": True,
    }

    assert articles[3]["slug"] == article2.slug
    assert articles[3]["title"] == article2.title
    assert articles[3]["description"] == article2.description
    assert articles[3]["body"] == article2.body
    assert articles[3]["tagList"] == article2.tag_list
    created_at = datetime.datetime.fromisoformat(articles[3]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[3]["updatedAt"])
    assert created_at == article2.created_at
    assert updated_at == article2.updated_at
    assert not articles[3]["favorited"]
    assert articles[3]["favoritesCount"] == 0
    assert articles[3]["author"] == {
        "username": author2.username,
        "bio": author2.bio,
        "image": author2.image,
        "following": True,
    }

    assert articles[4]["slug"] == article1.slug
    assert articles[4]["title"] == article1.title
    assert articles[4]["description"] == article1.description
    assert articles[4]["body"] == article1.body
    assert articles[4]["tagList"] == article1.tag_list
    created_at = datetime.datetime.fromisoformat(articles[4]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[4]["updatedAt"])
    assert created_at == article1.created_at
    assert updated_at == article1.updated_at
    assert not articles[4]["favorited"]
    assert articles[4]["favoritesCount"] == 0
    assert articles[4]["author"] == {
        "username": author1.username,
        "bio": author1.bio,
        "image": author1.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_all_query_args_but_offset_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user = await create_user_and_decode()

    author1 = await create_user_and_decode()
    author2 = await create_user_and_decode()
    author3 = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author1.token)
    article2 = await create_article_and_decode(author_token=author2.token)
    article3 = await create_article_and_decode(author_token=author3.token)
    article4 = await create_article_and_decode(author_token=author1.token)
    article5 = await create_article_and_decode(author_token=author2.token)
    article6 = await create_article_and_decode(author_token=author3.token)
    article7 = await create_article_and_decode(author_token=author1.token)
    article8 = await create_article_and_decode(author_token=author2.token)
    article9 = await create_article_and_decode(author_token=author3.token)

    await follow_user_and_decode(follower_token=user.token, username=author1.username)
    await follow_user_and_decode(follower_token=user.token, username=author2.username)

    await favorite_article_and_decode(user_token=user.token, slug=article5.slug)

    limit = 3

    response = await client.get(
        make_feed_articles_url(
            limit=limit,
        ),
        headers={
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == limit
    assert articles_count == limit

    assert articles[0]["slug"] == article8.slug
    assert articles[0]["title"] == article8.title
    assert articles[0]["description"] == article8.description
    assert articles[0]["body"] == article8.body
    assert articles[0]["tagList"] == article8.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article8.created_at
    assert updated_at == article8.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 0
    assert articles[0]["author"] == {
        "username": author2.username,
        "bio": author2.bio,
        "image": author2.image,
        "following": True,
    }

    assert articles[1]["slug"] == article7.slug
    assert articles[1]["title"] == article7.title
    assert articles[1]["description"] == article7.description
    assert articles[1]["body"] == article7.body
    assert articles[1]["tagList"] == article7.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article7.created_at
    assert updated_at == article7.updated_at
    assert not articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 0
    assert articles[1]["author"] == {
        "username": author1.username,
        "bio": author1.bio,
        "image": author1.image,
        "following": True,
    }

    assert articles[2]["slug"] == article5.slug
    assert articles[2]["title"] == article5.title
    assert articles[2]["description"] == article5.description
    assert articles[2]["body"] == article5.body
    assert articles[2]["tagList"] == article5.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article5.created_at
    assert updated_at == article5.updated_at
    assert articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 1
    assert articles[2]["author"] == {
        "username": author2.username,
        "bio": author2.bio,
        "image": author2.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_default_limit_should_be_20(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
):
    client = app.test_client()

    user = await create_user_and_decode()

    author1 = await create_user_and_decode()
    author2 = await create_user_and_decode()

    default_limit = 20
    created_articles = []
    for i in range(default_limit // 2):
        article1 = await create_article_and_decode(author_token=author1.token)
        article2 = await create_article_and_decode(author_token=author1.token)
        created_articles.append(article1)
        created_articles.append(article2)

    await follow_user_and_decode(follower_token=user.token, username=author1.username)
    await follow_user_and_decode(follower_token=user.token, username=author2.username)

    response = await client.get(
        make_feed_articles_url(),
        headers={
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == default_limit
    assert articles_count == default_limit

    assert articles[0]["slug"] == created_articles[-1].slug
    assert articles[-1]["slug"] == created_articles[0].slug


@pytest.mark.asyncio
async def test_when_token_is_not_sent_should_return_401(
    app,
    faker,
):
    client = app.test_client()

    response = await client.get(
        make_feed_articles_url(),
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=user.username, secret_key=secret_key)

    response = await client.get(
        make_feed_articles_url(),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_is_expired_should_return_401(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    token = create_jwt(username=user.username, expires_seconds=-1)

    response = await client.get(
        make_feed_articles_url(),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_user_is_not_found_should_return_401(app, faker):
    client = app.test_client()

    token = create_jwt(username=str(uuid.uuid4()))

    response = await client.get(
        make_feed_articles_url(),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
