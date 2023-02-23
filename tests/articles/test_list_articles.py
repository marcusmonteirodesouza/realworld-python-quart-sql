import pytest
import datetime
import secrets
import urllib.parse
import uuid
from typing import Optional
from ..utils import create_jwt


def make_list_articles_url(
    tag: Optional[str] = None,
    author: Optional[str] = None,
    favorited: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    params = {}

    if tag:
        params["tag"] = tag

    if author:
        params["author"] = author

    if favorited:
        params["favorited"] = favorited

    if limit:
        params["limit"] = limit

    if offset:
        params["offset"] = offset

    encoded_params = urllib.parse.urlencode(params)

    return f"/articles?{encoded_params}"


@pytest.mark.asyncio
async def test_when_token_is_sent_and_articles_are_favorited_and_authors_are_followed_and_all_query_args_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    tag = str(uuid.uuid4())

    author = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article2 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article3 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article4 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article5 = await create_article_and_decode(author_token=author.token, tags=[tag])

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    await favorite_article_and_decode(
        user_token=user1.token, article_slug=article3.slug
    )

    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article1.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article2.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article3.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article4.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article5.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    limit = 3
    offset = 1

    response = await client.get(
        make_list_articles_url(
            tag=tag,
            author=author.username,
            favorited=user2.username,
            limit=limit,
            offset=offset,
        ),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == limit
    assert articles_count == limit

    assert articles[0]["slug"] == article4.slug
    assert articles[0]["title"] == article4.title
    assert articles[0]["description"] == article4.description
    assert articles[0]["body"] == article4.body
    assert articles[0]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 1
    assert articles[0]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[1]["slug"] == article3.slug
    assert articles[1]["title"] == article3.title
    assert articles[1]["description"] == article3.description
    assert articles[1]["body"] == article3.body
    assert articles[1]["tagList"] == article3.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article3.created_at
    assert updated_at == article3.updated_at
    assert articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 2
    assert articles[1]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[2]["slug"] == article2.slug
    assert articles[2]["title"] == article2.title
    assert articles[2]["description"] == article2.description
    assert articles[2]["body"] == article2.body
    assert articles[2]["tagList"] == article2.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article2.created_at
    assert updated_at == article2.updated_at
    assert not articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 1
    assert articles[2]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_token_is_sent_and_articles_are_favorited_and_authors_are_followed_and_all_query_args_but_tag_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    author = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author.token)
    article2 = await create_article_and_decode(author_token=author.token)
    article3 = await create_article_and_decode(author_token=author.token)
    article4 = await create_article_and_decode(author_token=author.token)
    article5 = await create_article_and_decode(author_token=author.token)

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    await favorite_article_and_decode(
        user_token=user1.token, article_slug=article3.slug
    )

    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article1.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article2.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article3.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article4.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article5.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    limit = 3
    offset = 1

    response = await client.get(
        make_list_articles_url(
            author=author.username,
            favorited=user2.username,
            limit=limit,
            offset=offset,
        ),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == limit
    assert articles_count == limit

    assert articles[0]["slug"] == article4.slug
    assert articles[0]["title"] == article4.title
    assert articles[0]["description"] == article4.description
    assert articles[0]["body"] == article4.body
    assert articles[0]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 1
    assert articles[0]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[1]["slug"] == article3.slug
    assert articles[1]["title"] == article3.title
    assert articles[1]["description"] == article3.description
    assert articles[1]["body"] == article3.body
    assert articles[1]["tagList"] == article3.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article3.created_at
    assert updated_at == article3.updated_at
    assert articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 2
    assert articles[1]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[2]["slug"] == article2.slug
    assert articles[2]["title"] == article2.title
    assert articles[2]["description"] == article2.description
    assert articles[2]["body"] == article2.body
    assert articles[2]["tagList"] == article2.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article2.created_at
    assert updated_at == article2.updated_at
    assert not articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 1
    assert articles[2]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_token_is_sent_and_articles_are_favorited_and_authors_are_followed_and_all_query_args_but_author_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    tag = str(uuid.uuid4())

    author1 = await create_user_and_decode()
    author2 = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author1.token, tags=[tag])
    article2 = await create_article_and_decode(author_token=author2.token, tags=[tag])
    article3 = await create_article_and_decode(author_token=author1.token, tags=[tag])
    article4 = await create_article_and_decode(author_token=author2.token, tags=[tag])
    article5 = await create_article_and_decode(author_token=author1.token, tags=[tag])

    await follow_user_and_decode(follower_token=user1.token, username=author1.username)

    await favorite_article_and_decode(
        user_token=user1.token, article_slug=article3.slug
    )

    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article1.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article2.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article3.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article4.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article5.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=author1.username)

    limit = 3
    offset = 1

    response = await client.get(
        make_list_articles_url(
            tag=tag,
            favorited=user2.username,
            limit=limit,
            offset=offset,
        ),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == limit
    assert articles_count == limit

    assert articles[0]["slug"] == article4.slug
    assert articles[0]["title"] == article4.title
    assert articles[0]["description"] == article4.description
    assert articles[0]["body"] == article4.body
    assert articles[0]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 1
    assert articles[0]["author"] == {
        "username": author2.username,
        "bio": author2.bio,
        "image": author2.image,
        "following": False,
    }

    assert articles[1]["slug"] == article3.slug
    assert articles[1]["title"] == article3.title
    assert articles[1]["description"] == article3.description
    assert articles[1]["body"] == article3.body
    assert articles[1]["tagList"] == article3.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article3.created_at
    assert updated_at == article3.updated_at
    assert articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 2
    assert articles[1]["author"] == {
        "username": author1.username,
        "bio": author1.bio,
        "image": author1.image,
        "following": True,
    }

    assert articles[2]["slug"] == article2.slug
    assert articles[2]["title"] == article2.title
    assert articles[2]["description"] == article2.description
    assert articles[2]["body"] == article2.body
    assert articles[2]["tagList"] == article2.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article2.created_at
    assert updated_at == article2.updated_at
    assert not articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 1
    assert articles[2]["author"] == {
        "username": author2.username,
        "bio": author2.bio,
        "image": author2.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_token_is_sent_and_articles_are_favorited_and_authors_are_followed_and_all_query_args_but_favorited_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    tag = str(uuid.uuid4())

    author = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article2 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article3 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article4 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article5 = await create_article_and_decode(author_token=author.token, tags=[tag])

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    await favorite_article_and_decode(
        user_token=user1.token, article_slug=article3.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    limit = 3
    offset = 1

    response = await client.get(
        make_list_articles_url(
            tag=tag,
            author=author.username,
            limit=limit,
            offset=offset,
        ),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == limit
    assert articles_count == limit

    assert articles[0]["slug"] == article4.slug
    assert articles[0]["title"] == article4.title
    assert articles[0]["description"] == article4.description
    assert articles[0]["body"] == article4.body
    assert articles[0]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 0
    assert articles[0]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[1]["slug"] == article3.slug
    assert articles[1]["title"] == article3.title
    assert articles[1]["description"] == article3.description
    assert articles[1]["body"] == article3.body
    assert articles[1]["tagList"] == article3.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article3.created_at
    assert updated_at == article3.updated_at
    assert articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 1
    assert articles[1]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[2]["slug"] == article2.slug
    assert articles[2]["title"] == article2.title
    assert articles[2]["description"] == article2.description
    assert articles[2]["body"] == article2.body
    assert articles[2]["tagList"] == article2.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article2.created_at
    assert updated_at == article2.updated_at
    assert not articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 0
    assert articles[2]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_token_is_sent_and_articles_are_favorited_and_authors_are_followed_and_all_query_args_but_limit_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    tag = str(uuid.uuid4())

    author = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article2 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article3 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article4 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article5 = await create_article_and_decode(author_token=author.token, tags=[tag])

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    await favorite_article_and_decode(
        user_token=user1.token, article_slug=article3.slug
    )

    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article1.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article2.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article3.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article4.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article5.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    offset = 1

    response = await client.get(
        make_list_articles_url(
            tag=tag,
            author=author.username,
            favorited=user2.username,
            offset=offset,
        ),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == 4
    assert articles_count == 4

    assert articles[0]["slug"] == article4.slug
    assert articles[0]["title"] == article4.title
    assert articles[0]["description"] == article4.description
    assert articles[0]["body"] == article4.body
    assert articles[0]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 1
    assert articles[0]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[1]["slug"] == article3.slug
    assert articles[1]["title"] == article3.title
    assert articles[1]["description"] == article3.description
    assert articles[1]["body"] == article3.body
    assert articles[1]["tagList"] == article3.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article3.created_at
    assert updated_at == article3.updated_at
    assert articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 2
    assert articles[1]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[2]["slug"] == article2.slug
    assert articles[2]["title"] == article2.title
    assert articles[2]["description"] == article2.description
    assert articles[2]["body"] == article2.body
    assert articles[2]["tagList"] == article2.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article2.created_at
    assert updated_at == article2.updated_at
    assert not articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 1
    assert articles[2]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[3]["slug"] == article1.slug
    assert articles[3]["title"] == article1.title
    assert articles[3]["description"] == article1.description
    assert articles[3]["body"] == article1.body
    assert articles[3]["tagList"] == article1.tag_list
    created_at = datetime.datetime.fromisoformat(articles[3]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[3]["updatedAt"])
    assert created_at == article1.created_at
    assert updated_at == article1.updated_at
    assert not articles[3]["favorited"]
    assert articles[3]["favoritesCount"] == 1
    assert articles[3]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_when_token_is_sent_and_articles_are_favorited_and_authors_are_followed_and_all_query_args_but_offset_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    tag = str(uuid.uuid4())

    author = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article2 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article3 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article4 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article5 = await create_article_and_decode(author_token=author.token, tags=[tag])

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    await favorite_article_and_decode(
        user_token=user1.token, article_slug=article3.slug
    )

    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article1.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article2.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article3.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article4.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article5.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    limit = 3

    response = await client.get(
        make_list_articles_url(
            tag=tag,
            author=author.username,
            favorited=user2.username,
            limit=limit,
        ),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == limit
    assert articles_count == limit

    assert articles[0]["slug"] == article5.slug
    assert articles[0]["title"] == article5.title
    assert articles[0]["description"] == article5.description
    assert articles[0]["body"] == article5.body
    assert articles[0]["tagList"] == article5.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article5.created_at
    assert updated_at == article5.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 1
    assert articles[0]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[1]["slug"] == article4.slug
    assert articles[1]["title"] == article4.title
    assert articles[1]["description"] == article4.description
    assert articles[1]["body"] == article4.body
    assert articles[1]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 1
    assert articles[1]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }

    assert articles[2]["slug"] == article3.slug
    assert articles[2]["title"] == article3.title
    assert articles[2]["description"] == article3.description
    assert articles[2]["body"] == article3.body
    assert articles[2]["tagList"] == article3.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article3.created_at
    assert updated_at == article3.updated_at
    assert articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 2
    assert articles[2]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": True,
    }


@pytest.mark.asyncio
async def test_default_limit_should_be_20(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
):
    client = app.test_client()

    user = await create_user_and_decode()

    author = await create_user_and_decode()

    default_limit = 20
    created_articles = []

    for i in range(default_limit):
        article = await create_article_and_decode(author_token=author.token)
        created_articles.append(article)

    response = await client.get(
        make_list_articles_url(),
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
async def test_when_token_is_not_sent_and_articles_are_favorited_and_authors_are_followed_and_all_query_args_are_set_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    favorite_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    tag = str(uuid.uuid4())

    author = await create_user_and_decode()

    article1 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article2 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article3 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article4 = await create_article_and_decode(author_token=author.token, tags=[tag])
    article5 = await create_article_and_decode(author_token=author.token, tags=[tag])

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    await favorite_article_and_decode(
        user_token=user1.token, article_slug=article3.slug
    )

    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article1.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article2.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article3.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article4.slug
    )
    await favorite_article_and_decode(
        user_token=user2.token, article_slug=article5.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=author.username)

    limit = 3
    offset = 1

    response = await client.get(
        make_list_articles_url(
            tag=tag,
            author=author.username,
            favorited=user2.username,
            limit=limit,
            offset=offset,
        ),
    )

    assert response.status_code == 200

    response_data = await response.json

    articles = response_data["articles"]
    articles_count = response_data["articlesCount"]

    assert len(articles) == limit
    assert articles_count == limit

    assert articles[0]["slug"] == article4.slug
    assert articles[0]["title"] == article4.title
    assert articles[0]["description"] == article4.description
    assert articles[0]["body"] == article4.body
    assert articles[0]["tagList"] == article4.tag_list
    created_at = datetime.datetime.fromisoformat(articles[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[0]["updatedAt"])
    assert created_at == article4.created_at
    assert updated_at == article4.updated_at
    assert not articles[0]["favorited"]
    assert articles[0]["favoritesCount"] == 1
    assert articles[0]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": False,
    }

    assert articles[1]["slug"] == article3.slug
    assert articles[1]["title"] == article3.title
    assert articles[1]["description"] == article3.description
    assert articles[1]["body"] == article3.body
    assert articles[1]["tagList"] == article3.tag_list
    created_at = datetime.datetime.fromisoformat(articles[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[1]["updatedAt"])
    assert created_at == article3.created_at
    assert updated_at == article3.updated_at
    assert not articles[1]["favorited"]
    assert articles[1]["favoritesCount"] == 2
    assert articles[1]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": False,
    }

    assert articles[2]["slug"] == article2.slug
    assert articles[2]["title"] == article2.title
    assert articles[2]["description"] == article2.description
    assert articles[2]["body"] == article2.body
    assert articles[2]["tagList"] == article2.tag_list
    created_at = datetime.datetime.fromisoformat(articles[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(articles[2]["updatedAt"])
    assert created_at == article2.created_at
    assert updated_at == article2.updated_at
    assert not articles[2]["favorited"]
    assert articles[2]["favoritesCount"] == 1
    assert articles[2]["author"] == {
        "username": author.username,
        "bio": author.bio,
        "image": author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=user.username, secret_key=secret_key)

    response = await client.get(
        make_list_articles_url(),
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
        make_list_articles_url(),
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
        make_list_articles_url(),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
