import pytest
import json
import secrets
from ..utils import create_jwt


@pytest.mark.asyncio
async def test_when_all_fields_set_should_return_200(app, faker, user):
    client = app.test_client()

    update_user_data = {
        "user": {
            "username": faker.user_name(),
            "email": faker.email(),
            "password": faker.password(),
            "bio": faker.paragraph(),
            "image": faker.url(),
        }
    }

    login_data = {
        "user": {
            "email": update_user_data["user"]["email"],
            "password": update_user_data["user"]["password"],
        }
    }

    update_user_response = await client.put(
        "/user",
        data=json.dumps(update_user_data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    login_response = await client.post(
        "/users/login",
        data=json.dumps(login_data),
        headers={"Content-Type": "application/json"},
    )

    assert update_user_response.status_code == 200

    assert login_response.status_code == 200

    update_user_response_data = await update_user_response.json

    updated_user = update_user_response_data["user"]

    assert updated_user["username"] == update_user_data["user"]["username"]
    assert updated_user["email"] == update_user_data["user"]["email"]
    assert updated_user["token"] == user.token
    assert updated_user["bio"] == update_user_data["user"]["bio"]
    assert updated_user["image"] == update_user_data["user"]["image"]


@pytest.mark.asyncio
async def test_when_username_is_set_should_return_200(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "username": faker.user_name(),
        }
    }

    response = await client.put(
        "/user",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_user = response_data["user"]

    assert updated_user["username"] == data["user"]["username"]
    assert updated_user["email"] == user.email
    assert updated_user["token"] == user.token
    assert updated_user["bio"] == user.bio
    assert updated_user["image"] == user.image


@pytest.mark.asyncio
async def test_when_email_is_set_should_return_200(app, faker, user):
    client = app.test_client()

    update_user_data = {
        "user": {
            "email": faker.email(),
        }
    }

    login_data = {
        "user": {"email": update_user_data["user"]["email"], "password": user.password}
    }

    update_user_response = await client.put(
        "/user",
        data=json.dumps(update_user_data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    login_response = await client.post(
        "/users/login",
        data=json.dumps(login_data),
        headers={"Content-Type": "application/json"},
    )

    assert update_user_response.status_code == 200

    assert login_response.status_code == 200

    update_user_response_data = await update_user_response.json

    updated_user = update_user_response_data["user"]

    assert updated_user["username"] == user.username
    assert updated_user["email"] == update_user_data["user"]["email"]
    assert updated_user["token"] == user.token
    assert updated_user["bio"] == user.bio
    assert updated_user["image"] == user.image


@pytest.mark.asyncio
async def test_when_password_is_set_should_return_200(app, faker, user):
    client = app.test_client()

    update_user_data = {
        "user": {
            "password": faker.password(),
        }
    }

    login_data = {
        "user": {"email": user.email, "password": update_user_data["user"]["password"]}
    }

    update_user_response = await client.put(
        "/user",
        data=json.dumps(update_user_data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    login_response = await client.post(
        "/users/login",
        data=json.dumps(login_data),
        headers={"Content-Type": "application/json"},
    )

    assert update_user_response.status_code == 200

    assert login_response.status_code == 200

    update_user_response_data = await update_user_response.json

    updated_user = update_user_response_data["user"]

    assert updated_user["username"] == user.username
    assert updated_user["email"] == user.email
    assert updated_user["token"] == user.token
    assert updated_user["bio"] == user.bio
    assert updated_user["image"] == user.image


@pytest.mark.asyncio
async def test_when_bio_is_set_should_return_200(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "bio": faker.paragraph(),
        }
    }

    response = await client.put(
        "/user",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_user = response_data["user"]

    assert updated_user["username"] == user.username
    assert updated_user["email"] == user.email
    assert updated_user["token"] == user.token
    assert updated_user["bio"] == data["user"]["bio"]
    assert updated_user["image"] == user.image


@pytest.mark.asyncio
async def test_when_image_is_set_should_return_200(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "image": faker.url(),
        }
    }

    response = await client.put(
        "/user",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {user.token}",
        },
    )

    assert response.status_code == 200

    response_data = await response.json

    updated_user = response_data["user"]

    assert updated_user["username"] == user.username
    assert updated_user["email"] == user.email
    assert updated_user["token"] == user.token
    assert updated_user["bio"] == user.bio
    assert updated_user["image"] == data["user"]["image"]


@pytest.mark.asyncio
async def test_when_authorization_header_is_not_set_should_return_401(app, faker):
    client = app.test_client()

    response = await client.put("/user")

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, faker, user
):
    client = app.test_client()

    response = await client.put(
        "/user",
        headers={"Authorization": f"Bearer {user.token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(app, faker, user):
    client = app.test_client()

    secret_key = secrets.token_urlsafe()

    token = create_jwt(username=user.username, secret_key=secret_key)

    response = await client.put(
        "/user",
        headers={"Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_is_expired_should_return_401(app, faker, user):
    client = app.test_client()

    token = create_jwt(username=user.username, expires_seconds=-1)

    response = await client.put(
        "/user",
        headers={"Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_user_is_not_found_should_return_401(app, faker):
    client = app.test_client()

    token = create_jwt(username=faker.user_name())

    data = {
        "user": {
            "email": faker.email(),
            "password": faker.password(),
            "username": faker.user_name(),
            "bio": faker.paragraph(),
            "image": faker.url(),
        }
    }

    response = await client.put(
        "/user",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
