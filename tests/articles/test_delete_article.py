import pytest
import secrets
import uuid
from ..utils import create_jwt


def make_delete_article_url(slug: str) -> str:
    return f"/articles/{slug}"


@pytest.mark.asyncio
async def test_should_return_204(
    app, faker, create_user_and_decode, create_article_and_decode, get_article
):
    client = app.test_client()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    response = await client.delete(
        make_delete_article_url(slug=article.slug),
        headers={
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 204

    response_data = await response.json

    assert response_data is None

    get_article_response = await get_article(slug=article.slug)

    assert get_article_response.status_code == 404

    get_article_response_data = await get_article_response.json

    assert (
        get_article_response_data["errors"]["body"][0]
        == f"slug {article.slug} not found"
    )


@pytest.mark.asyncio
async def test_when_article_is_not_found_should_return_404(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    author = await create_user_and_decode()

    slug = str(uuid.uuid4())

    response = await client.delete(
        make_delete_article_url(slug=slug),
        headers={
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 404

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"slug {slug} not found"


@pytest.mark.asyncio
async def test_when_user_is_not_the_author_should_return_401(
    app, faker, create_user_and_decode, create_article_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    response = await client.delete(
        make_delete_article_url(slug=article.slug),
        headers={
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"unauthorized"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, faker, create_user_and_decode, create_article_and_decode
):
    client = app.test_client()

    author = await create_user_and_decode()

    article = await create_article_and_decode(author_token=author.token)

    response = await client.delete(
        make_delete_article_url(slug=article.slug),
        headers={
            "Authorization": f"Bearer {author.token}",
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
        make_delete_article_url(slug=created_article.slug),
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
        make_delete_article_url(slug=created_article.slug),
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
        make_delete_article_url(slug=created_article.slug),
        headers={
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
