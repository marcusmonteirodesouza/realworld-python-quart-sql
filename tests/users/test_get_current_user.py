import pytest
import secrets
from ..utils import create_jwt


def make_get_current_user_url():
    return "/api/user"


@pytest.mark.asyncio
async def test_should_return_200(app, faker, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

    response = await client.get(
        make_get_current_user_url(),
        headers={"Authorization": f"Token {user.token}"},
    )

    assert response.status_code == 200

    response_data = await response.json

    current_user = response_data["user"]

    assert current_user["username"] == user.username
    assert current_user["email"] == user.email
    assert current_user["token"] == user.token
    assert current_user["bio"] == user.bio
    assert current_user["image"] == user.image


@pytest.mark.asyncio
async def test_when_authorization_header_is_not_set_should_return_401(app, faker):
    client = app.test_client()

    response = await client.get(make_get_current_user_url())

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    response = await client.get(
        make_get_current_user_url(),
        headers={"Authorization": f"Bearer {user.token}"},
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
        make_get_current_user_url(),
        headers={"Authorization": f"Token {token}"},
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
        make_get_current_user_url(),
        headers={"Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_user_is_not_found_should_return_401(app, faker):
    client = app.test_client()

    token = create_jwt(username=faker.user_name())

    response = await client.get(
        make_get_current_user_url(),
        headers={"Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
