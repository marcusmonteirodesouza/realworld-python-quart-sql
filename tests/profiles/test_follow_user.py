import pytest
import secrets
import uuid
from ..utils import create_jwt


def make_follow_user_url(followed_username: str) -> str:
    return f"/profiles/{followed_username}/follow"


@pytest.mark.asyncio
async def test_when_authorization_header_is_not_set_should_return_401(app, create_user):
    client = app.test_client()

    followed = await create_user()

    response = await client.post(
        make_follow_user_url(followed_username=followed.username)
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, create_user
):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    response = await client.post(
        make_follow_user_url(followed_username=followed.username),
        headers={"Authorization": f"Bearer {follower.token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(app, create_user):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=follower.username, secret_key=secret_key)

    response = await client.post(
        make_follow_user_url(followed_username=followed.username),
        headers={"Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_is_expired_should_return_401(app, create_user):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    token = create_jwt(username=follower.username, expires_seconds=-1)

    response = await client.post(
        make_follow_user_url(followed_username=followed.username),
        headers={"Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_user_is_not_found_should_return_401(app, faker, create_user):
    client = app.test_client()

    token = create_jwt(username=str(uuid.uuid4()))

    followed = await create_user()

    response = await client.post(
        make_follow_user_url(followed_username=followed.username),
        headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
