import pytest
import secrets
import uuid
from ..utils import create_jwt


def make_get_profile_url(username: str) -> str:
    return f"/profiles/{username}"


@pytest.mark.asyncio
async def test_when_user_is_followed_and_valid_token_should_return_200(
    app, create_user, follow_user
):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    await follow_user(follower_token=follower.token, username=followed.username)

    response = await client.get(
        make_get_profile_url(username=followed.username),
        headers={"Authorization": f"Token {follower.token}"},
    )

    assert response.status_code == 200

    response_data = await response.json

    profile = response_data["profile"]

    assert profile["username"] == followed.username
    assert profile["bio"] == followed.bio
    assert profile["image"] == followed.image
    assert profile["following"]


@pytest.mark.asyncio
async def test_when_user_is_not_followed_and_valid_token_should_return_200(
    app, create_user
):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    response = await client.get(
        make_get_profile_url(username=followed.username),
        headers={"Authorization": f"Token {follower.token}"},
    )

    assert response.status_code == 200

    response_data = await response.json

    profile = response_data["profile"]

    assert profile["username"] == followed.username
    assert profile["bio"] == followed.bio
    assert profile["image"] == followed.image
    assert not profile["following"]


@pytest.mark.asyncio
async def test_when_user_is_not_found_and_valid_token_should_return_404(
    app, create_user
):
    client = app.test_client()

    follower = await create_user()

    followed_username = str(uuid.uuid4())

    response = await client.get(
        make_get_profile_url(username=followed_username),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {follower.token}",
        },
    )

    assert response.status_code == 404

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"user {followed_username} not found"


@pytest.mark.asyncio
async def test_when_user_is_not_found_and_no_token_should_return_404(app, create_user):
    client = app.test_client()

    followed_username = str(uuid.uuid4())

    response = await client.get(
        make_get_profile_url(username=followed_username),
    )

    assert response.status_code == 404

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"user {followed_username} not found"


@pytest.mark.asyncio
async def test_when_follower_is_not_found_and_valid_token_should_return_401(
    app, faker, create_user
):
    client = app.test_client()

    token = create_jwt(username=str(uuid.uuid4()))

    followed = await create_user()

    response = await client.get(
        make_get_profile_url(username=followed.username),
        headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_200(
    app, create_user, follow_user
):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    await follow_user(follower_token=follower.token, username=followed.username)

    response = await client.get(
        make_get_profile_url(username=followed.username),
        headers={"Authorization": f"Bearer {follower.token}"},
    )

    assert response.status_code == 200

    response_data = await response.json

    profile = response_data["profile"]

    assert profile["username"] == followed.username
    assert profile["bio"] == followed.bio
    assert profile["image"] == followed.image
    assert not profile["following"]


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(app, create_user):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=follower.username, secret_key=secret_key)

    response = await client.get(
        make_get_profile_url(username=followed.username),
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

    response = await client.get(
        make_get_profile_url(username=followed.username),
        headers={"Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
