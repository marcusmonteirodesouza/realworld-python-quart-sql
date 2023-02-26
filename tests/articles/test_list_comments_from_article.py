import pytest
import datetime
import secrets
import uuid
from ..utils import create_jwt


def make_list_comments_from_article_url(slug: str):
    return f"/api/articles/{slug}/comments"


@pytest.mark.asyncio
async def test_when_token_is_sent_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    add_comment_to_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()
    user3 = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    comment1 = await add_comment_to_article_and_decode(
        author_token=user1.token, slug=article.slug
    )
    comment2 = await add_comment_to_article_and_decode(
        author_token=user2.token, slug=article.slug
    )
    comment3 = await add_comment_to_article_and_decode(
        author_token=user3.token, slug=article.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=user3.username)

    response = await client.get(
        make_list_comments_from_article_url(
            slug=article.slug,
        ),
        headers={
            "Authorization": f"Token {user1.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    comments = response_data["comments"]

    assert len(comments) == 3

    assert comments[0]["id"] == comment3.id
    assert comments[0]["body"] == comment3.body
    created_at = datetime.datetime.fromisoformat(comments[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(comments[0]["updatedAt"])
    assert created_at == comment3.created_at
    assert updated_at == comment3.updated_at
    assert comments[0]["author"] == {
        "username": comment3.author.username,
        "bio": comment3.author.bio,
        "image": comment3.author.image,
        "following": True,
    }

    assert comments[1]["id"] == comment2.id
    assert comments[1]["body"] == comment2.body
    created_at = datetime.datetime.fromisoformat(comments[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(comments[1]["updatedAt"])
    assert created_at == comment2.created_at
    assert updated_at == comment2.updated_at
    assert comments[1]["author"] == {
        "username": comment2.author.username,
        "bio": comment2.author.bio,
        "image": comment2.author.image,
        "following": False,
    }

    assert comments[2]["id"] == comment1.id
    assert comments[2]["body"] == comment1.body
    created_at = datetime.datetime.fromisoformat(comments[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(comments[2]["updatedAt"])
    assert created_at == comment1.created_at
    assert updated_at == comment1.updated_at
    assert comments[2]["author"] == {
        "username": comment1.author.username,
        "bio": comment1.author.bio,
        "image": comment1.author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_token_is_not_sent_should_return_200(
    app,
    faker,
    create_user_and_decode,
    follow_user_and_decode,
    create_article_and_decode,
    add_comment_to_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()
    user3 = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    comment1 = await add_comment_to_article_and_decode(
        author_token=user1.token, slug=article.slug
    )
    comment2 = await add_comment_to_article_and_decode(
        author_token=user2.token, slug=article.slug
    )
    comment3 = await add_comment_to_article_and_decode(
        author_token=user3.token, slug=article.slug
    )

    await follow_user_and_decode(follower_token=user1.token, username=user3.username)

    response = await client.get(
        make_list_comments_from_article_url(
            slug=article.slug,
        ),
    )

    assert response.status_code == 200

    response_data = await response.json

    comments = response_data["comments"]

    assert len(comments) == 3

    assert comments[0]["id"] == comment3.id
    assert comments[0]["body"] == comment3.body
    created_at = datetime.datetime.fromisoformat(comments[0]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(comments[0]["updatedAt"])
    assert created_at == comment3.created_at
    assert updated_at == comment3.updated_at
    assert comments[0]["author"] == {
        "username": comment3.author.username,
        "bio": comment3.author.bio,
        "image": comment3.author.image,
        "following": False,
    }

    assert comments[1]["id"] == comment2.id
    assert comments[1]["body"] == comment2.body
    created_at = datetime.datetime.fromisoformat(comments[1]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(comments[1]["updatedAt"])
    assert created_at == comment2.created_at
    assert updated_at == comment2.updated_at
    assert comments[1]["author"] == {
        "username": comment2.author.username,
        "bio": comment2.author.bio,
        "image": comment2.author.image,
        "following": False,
    }

    assert comments[2]["id"] == comment1.id
    assert comments[2]["body"] == comment1.body
    created_at = datetime.datetime.fromisoformat(comments[2]["createdAt"])
    updated_at = datetime.datetime.fromisoformat(comments[2]["updatedAt"])
    assert created_at == comment1.created_at
    assert updated_at == comment1.updated_at
    assert comments[2]["author"] == {
        "username": comment1.author.username,
        "bio": comment1.author.bio,
        "image": comment1.author.image,
        "following": False,
    }


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app, faker, create_user_and_decode, create_article_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=user.username, secret_key=secret_key)

    response = await client.get(
        make_list_comments_from_article_url(slug=article.slug),
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

    user = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    token = create_jwt(username=user.username, expires_seconds=-1)

    response = await client.get(
        make_list_comments_from_article_url(slug=article.slug),
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

    article = await create_article_and_decode(author_token=author.token)

    token = create_jwt(username=str(uuid.uuid4()))

    response = await client.get(
        make_list_comments_from_article_url(slug=article.slug),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
