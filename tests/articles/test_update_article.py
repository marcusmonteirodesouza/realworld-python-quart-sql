import pytest
import datetime
import json
import re
import secrets
import uuid
from ..utils import create_jwt


def make_update_article_url(slug: str) -> str:
    return f"/articles/{slug}"


@pytest.mark.asyncio
async def test_when_all_data_is_set_should_return_200(
    app, faker, create_user, create_article, get_article_and_decode
):
    client = app.test_client()

    author = await create_user()

    article = await create_article(author_token=author.token)

    data = {
        "article": {
            "title": "I'm changing the title here!",
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

    response = await client.put(
        make_update_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_article = response_data["article"]

    assert re.match(r"im-changing-the-title-here-\S+", updated_article["slug"])
    assert updated_article["title"] == data["article"]["title"]
    assert updated_article["description"] == data["article"]["description"]
    assert updated_article["body"] == data["article"]["body"]
    assert updated_article["tagList"] == [
        "123",
        "dragons",
        "repeated",
        "some-spaces",
        "training",
    ]
    created_at = datetime.datetime.fromisoformat(updated_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(updated_article["updatedAt"])
    assert updated_at > created_at

    got_article = await get_article_and_decode(slug=updated_article["slug"])

    assert updated_article["title"] == got_article.title
    assert updated_article["description"] == got_article.description
    assert updated_article["body"] == got_article.body
    assert updated_article["tagList"] == got_article.tag_list
    assert created_at == got_article.created_at
    assert updated_at == got_article.updated_at


@pytest.mark.asyncio
async def test_when_title_is_set_should_return_200(
    app, faker, create_user, create_article, get_article_and_decode
):
    client = app.test_client()

    author = await create_user()

    article = await create_article(author_token=author.token)

    data = {
        "article": {
            "title": "I'm changing the title here!",
        }
    }

    response = await client.put(
        make_update_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_article = response_data["article"]

    assert re.match(r"im-changing-the-title-here-\S+", updated_article["slug"])
    assert updated_article["title"] == data["article"]["title"]
    created_at = datetime.datetime.fromisoformat(updated_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(updated_article["updatedAt"])
    assert updated_at > created_at

    got_article = await get_article_and_decode(slug=updated_article["slug"])

    assert updated_article["title"] == got_article.title
    assert updated_article["description"] == got_article.description
    assert updated_article["body"] == got_article.body
    assert updated_article["tagList"] == got_article.tag_list
    assert created_at == got_article.created_at
    assert updated_at == got_article.updated_at


@pytest.mark.asyncio
async def test_when_description_is_set_should_return_200(
    app, faker, create_user, create_article, get_article_and_decode
):
    client = app.test_client()

    author = await create_user()

    article = await create_article(author_token=author.token)

    data = {
        "article": {
            "description": faker.sentence(),
        }
    }

    response = await client.put(
        make_update_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_article = response_data["article"]

    assert updated_article["slug"] == article.slug
    assert updated_article["description"] == data["article"]["description"]
    created_at = datetime.datetime.fromisoformat(updated_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(updated_article["updatedAt"])
    assert updated_at > created_at

    got_article = await get_article_and_decode(slug=updated_article["slug"])

    assert updated_article["title"] == got_article.title
    assert updated_article["description"] == got_article.description
    assert updated_article["body"] == got_article.body
    assert updated_article["tagList"] == got_article.tag_list
    assert created_at == got_article.created_at
    assert updated_at == got_article.updated_at


@pytest.mark.asyncio
async def test_when_body_is_set_should_return_200(
    app, faker, create_user, create_article, get_article_and_decode
):
    client = app.test_client()

    author = await create_user()

    article = await create_article(author_token=author.token)

    data = {
        "article": {
            "body": faker.paragraph(),
        }
    }

    response = await client.put(
        make_update_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_article = response_data["article"]

    assert updated_article["slug"] == article.slug
    assert updated_article["body"] == data["article"]["body"]
    created_at = datetime.datetime.fromisoformat(updated_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(updated_article["updatedAt"])
    assert updated_at > created_at

    got_article = await get_article_and_decode(slug=updated_article["slug"])

    assert updated_article["title"] == got_article.title
    assert updated_article["description"] == got_article.description
    assert updated_article["body"] == got_article.body
    assert updated_article["tagList"] == got_article.tag_list
    assert created_at == got_article.created_at
    assert updated_at == got_article.updated_at


@pytest.mark.asyncio
async def test_when_tagList_is_set_should_return_200(
    app, faker, create_user, create_article, get_article_and_decode
):
    client = app.test_client()

    author = await create_user()

    article = await create_article(author_token=author.token)

    data = {
        "article": {
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

    response = await client.put(
        make_update_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_article = response_data["article"]

    assert updated_article["slug"] == article.slug
    assert updated_article["tagList"] == [
        "123",
        "dragons",
        "repeated",
        "some-spaces",
        "training",
    ]
    created_at = datetime.datetime.fromisoformat(updated_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(updated_article["updatedAt"])
    assert updated_at == created_at

    got_article = await get_article_and_decode(slug=updated_article["slug"])

    assert updated_article["title"] == got_article.title
    assert updated_article["description"] == got_article.description
    assert updated_article["body"] == got_article.body
    assert updated_article["tagList"] == got_article.tag_list
    assert created_at == got_article.created_at
    assert updated_at == got_article.updated_at


@pytest.mark.asyncio
async def test_when_no_data_is_set_should_return_200(
    app, faker, create_user, create_article, get_article_and_decode
):
    client = app.test_client()

    author = await create_user()

    article = await create_article(author_token=author.token)

    data = {"article": {}}

    response = await client.put(
        make_update_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_article = response_data["article"]

    assert updated_article["slug"] == article.slug
    created_at = datetime.datetime.fromisoformat(updated_article["createdAt"])
    updated_at = datetime.datetime.fromisoformat(updated_article["updatedAt"])
    assert updated_at == created_at

    got_article = await get_article_and_decode(slug=updated_article["slug"])

    assert updated_article["title"] == got_article.title
    assert updated_article["description"] == got_article.description
    assert updated_article["body"] == got_article.body
    assert updated_article["tagList"] == got_article.tag_list
    assert created_at == got_article.created_at
    assert updated_at == got_article.updated_at


@pytest.mark.asyncio
async def test_when_article_is_not_found_should_return_404(app, faker, create_user):
    client = app.test_client()

    author = await create_user()

    slug = str(uuid.uuid4())

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10),
        }
    }

    response = await client.put(
        make_update_article_url(slug=slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {author.token}",
        },
    )

    assert response.status_code == 404

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"slug {slug} not found"


@pytest.mark.asyncio
async def test_when_user_is_not_the_author_should_return_401(
    app, faker, create_user, create_article
):
    client = app.test_client()

    user = await create_user()

    author = await create_user()

    article = await create_article(author_token=author.token)

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10),
        }
    }

    response = await client.put(
        make_update_article_url(slug=article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"unauthorized"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, faker, create_user, create_article
):
    client = app.test_client()

    author = await create_user()

    article = await create_article(author_token=author.token)

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10, unique=True),
        }
    }

    response = await client.put(
        make_update_article_url(slug=article.slug),
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
    app, faker, create_user, create_article
):
    client = app.test_client()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=author.username, secret_key=secret_key)

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10, unique=True),
        }
    }

    response = await client.put(
        make_update_article_url(slug=created_article.slug),
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
    app, faker, create_user, create_article
):
    client = app.test_client()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    token = create_jwt(username=author.username, expires_seconds=-1)

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10, unique=True),
        }
    }

    response = await client.put(
        make_update_article_url(slug=created_article.slug),
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
    app, faker, create_user, create_article
):
    client = app.test_client()

    author = await create_user()

    created_article = await create_article(author_token=author.token)

    token = create_jwt(username=str(uuid.uuid4()))

    data = {
        "article": {
            "title": faker.sentence(),
            "description": faker.sentence(),
            "body": faker.paragraph(),
            "tagList": faker.words(nb=10),
        }
    }

    response = await client.put(
        make_update_article_url(slug=created_article.slug),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
