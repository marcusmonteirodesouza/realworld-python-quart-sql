import pytest
import secrets
from ..utils import create_jwt


def make_delete_comment_from_article_url(slug: str, comment_id: str):
    return f"/articles/{slug}/comments/{comment_id}"


@pytest.mark.asyncio
async def test_when_token_is_sent_should_return_204(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
    add_comment_to_article_and_decode,
    list_comments_from_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    comment1 = await add_comment_to_article_and_decode(
        author_token=user1.token, slug=article.slug
    )
    comment2 = await add_comment_to_article_and_decode(
        author_token=user2.token, slug=article.slug
    )

    response = await client.delete(
        make_delete_comment_from_article_url(slug=article.slug, comment_id=comment2.id),
        headers={
            "Authorization": f"Token {user2.token}",
        },
    )

    assert response.status_code == 204

    comments = await list_comments_from_article_and_decode(
        slug=article.slug, user_token=user1.token
    )

    assert len(comments) == 1

    assert comments[0].id == comment1.id


@pytest.mark.asyncio
async def test_when_user_is_not_the_comment_author_should_return_401(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
    add_comment_to_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    comment = await add_comment_to_article_and_decode(
        author_token=user1.token, slug=article.slug
    )

    response = await client.delete(
        make_delete_comment_from_article_url(slug=article.slug, comment_id=comment.id),
        headers={
            "Authorization": f"Token {user2.token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_is_not_sent_should_return_401(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
    add_comment_to_article_and_decode,
):
    client = app.test_client()

    user1 = await create_user_and_decode()
    user2 = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    comment1 = await add_comment_to_article_and_decode(
        author_token=user1.token, slug=article.slug
    )
    comment2 = await add_comment_to_article_and_decode(
        author_token=user2.token, slug=article.slug
    )

    response = await client.delete(
        make_delete_comment_from_article_url(slug=article.slug, comment_id=comment2.id),
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
    add_comment_to_article_and_decode,
):
    client = app.test_client()

    user = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    comment = await add_comment_to_article_and_decode(
        author_token=user.token, slug=article.slug
    )

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=user.username, secret_key=secret_key)

    response = await client.delete(
        make_delete_comment_from_article_url(slug=article.slug, comment_id=comment.id),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_is_expired_should_return_401(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
    add_comment_to_article_and_decode,
):
    client = app.test_client()

    user = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    comment = await add_comment_to_article_and_decode(
        author_token=user.token, slug=article.slug
    )

    token = create_jwt(username=user.username, expires_seconds=-1)

    response = await client.delete(
        make_delete_comment_from_article_url(slug=article.slug, comment_id=comment.id),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
