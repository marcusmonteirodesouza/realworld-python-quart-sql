import pytest
import secrets
import uuid
from ..utils import create_jwt


def make_follow_user_url(username: str) -> str:
    return f"/profiles/{username}/follow"


@pytest.mark.asyncio
async def test_should_return_200(app, create_user):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    response = await client.post(
        make_follow_user_url(username=followed.username),
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
async def test_when_user_is_already_followed_should_return_200(
    app, create_user, follow_user
):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    follow_user_profile = await follow_user(
        follower_token=follower.token, username=followed.username
    )

    response = await client.post(
        make_follow_user_url(username=followed.username),
        headers={"Authorization": f"Token {follower.token}"},
    )

    assert response.status_code == 200

    response_data = await response.json

    profile = response_data["profile"]

    assert profile["username"] == follow_user_profile.username
    assert profile["bio"] == follow_user_profile.bio
    assert profile["image"] == follow_user_profile.image
    assert profile["following"] and follow_user_profile.following


@pytest.mark.asyncio
async def test_when_user_was_unfollowed_should_return_200(
    app, create_user, follow_user, unfollow_user
):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    await follow_user(follower_token=follower.token, username=followed.username)

    await unfollow_user(follower_token=follower.token, username=followed.username)

    follow_user_profile = await follow_user(
        follower_token=follower.token, username=followed.username
    )

    response = await client.post(
        make_follow_user_url(username=followed.username),
        headers={"Authorization": f"Token {follower.token}"},
    )

    assert response.status_code == 200

    response_data = await response.json

    profile = response_data["profile"]

    assert profile["username"] == follow_user_profile.username
    assert profile["bio"] == follow_user_profile.bio
    assert profile["image"] == follow_user_profile.image
    assert profile["following"] and follow_user_profile.following


@pytest.mark.asyncio
async def test_when_user_is_not_found_should_return_404(app, create_user):
    client = app.test_client()

    follower = await create_user()

    followed_username = str(uuid.uuid4())

    response = await client.post(
        make_follow_user_url(username=followed_username),
        headers={"Authorization": f"Token {follower.token}"},
    )

    assert response.status_code == 404

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0] == f"username {followed_username} not found"
    )


@pytest.mark.asyncio
async def test_when_user_tries_to_follow_himself_should_return_422(app, create_user):
    client = app.test_client()

    follower = await create_user()

    response = await client.post(
        make_follow_user_url(username=follower.username),
        headers={"Authorization": f"Token {follower.token}"},
    )

    assert response.status_code == 422

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"user cannot follow him/herself"


@pytest.mark.asyncio
async def test_when_authorization_header_is_not_set_should_return_401(app, create_user):
    client = app.test_client()

    followed = await create_user()

    response = await client.post(make_follow_user_url(username=followed.username))

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
        make_follow_user_url(username=followed.username),
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
        make_follow_user_url(username=followed.username),
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
        make_follow_user_url(username=followed.username),
        headers={"Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_follower_is_not_found_should_return_401(app, faker, create_user):
    client = app.test_client()

    token = create_jwt(username=str(uuid.uuid4()))

    followed = await create_user()

    response = await client.post(
        make_follow_user_url(username=followed.username),
        headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
