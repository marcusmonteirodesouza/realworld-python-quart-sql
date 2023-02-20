import pytest
import json
import secrets
import uuid
from ..utils import create_jwt


@pytest.mark.asyncio
async def test_when_all_fields_set_should_return_200(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

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
async def test_when_username_is_set_should_return_200(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

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
async def test_when_username_is_taken_should_return_422(app, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

    existing_user = await create_user_and_decode()

    data = {
        "user": {
            "username": existing_user.username,
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

    assert response.status_code == 422

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"username is taken"


@pytest.mark.asyncio
async def test_when_email_is_set_should_return_200(app, faker, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

    update_user_data = {
        "user": {
            "email": faker.email(),
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

    assert update_user_response.status_code == 200

    update_user_response_data = await update_user_response.json

    updated_user = update_user_response_data["user"]

    assert updated_user["username"] == user.username
    assert updated_user["email"] == update_user_data["user"]["email"]
    assert updated_user["token"] == user.token
    assert updated_user["bio"] == user.bio
    assert updated_user["image"] == user.image

    login_data = {
        "user": {"email": update_user_data["user"]["email"], "password": user.password}
    }

    login_response = await client.post(
        "/users/login",
        data=json.dumps(login_data),
        headers={"Content-Type": "application/json"},
    )

    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_when_email_is_invalid_should_return_422(app, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

    data = {
        "user": {
            "email": "an-invalid-email",
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

    assert response.status_code == 422

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0] == f"invalid email {data['user']['email']}"
    )


@pytest.mark.asyncio
async def test_when_email_is_taken_should_return_422(app, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

    existing_user = await create_user_and_decode()

    data = {
        "user": {
            "email": existing_user.email,
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

    assert response.status_code == 422

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"email is taken"


@pytest.mark.asyncio
async def test_when_password_is_set_should_return_200(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    update_user_data = {
        "user": {
            "password": faker.password(),
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

    assert update_user_response.status_code == 200

    update_user_response_data = await update_user_response.json

    updated_user = update_user_response_data["user"]

    assert updated_user["username"] == user.username
    assert updated_user["email"] == user.email
    assert updated_user["token"] == user.token
    assert updated_user["bio"] == user.bio
    assert updated_user["image"] == user.image

    login_data = {
        "user": {"email": user.email, "password": update_user_data["user"]["password"]}
    }

    login_response = await client.post(
        "/users/login",
        data=json.dumps(login_data),
        headers={"Content-Type": "application/json"},
    )

    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_when_password_is_too_short_should_return_422(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    data = {
        "user": {
            "password": faker.password(length=7),
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

    assert response.status_code == 422

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "password length must be greater than or equal to 8"
    )


@pytest.mark.asyncio
async def test_when_password_is_too_long_should_return_422(
    app, faker, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    data = {
        "user": {
            "password": faker.password(length=65),
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

    assert response.status_code == 422

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "password length must be less than or equal to 64"
    )


@pytest.mark.asyncio
async def test_when_bio_is_set_should_return_200(app, faker, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

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
async def test_when_image_is_set_should_return_200(app, faker, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

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
async def test_when_image_is_invalid_should_return_422(app, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

    data = {
        "user": {
            "image": "not-an-url",
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

    assert response.status_code == 422

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == f"invalid image {data['user']['image']}. It must be a valid url"
    )


@pytest.mark.asyncio
async def test_when_authorization_header_is_not_set_should_return_401(app):
    client = app.test_client()

    response = await client.put("/user")

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_authorization_header_has_invalid_scheme_should_return_401(
    app, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

    response = await client.put(
        "/user",
        headers={"Authorization": f"Bearer {user.token}"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_token_has_invalid_signature_should_return_401(
    app, create_user_and_decode
):
    client = app.test_client()

    user = await create_user_and_decode()

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
async def test_when_token_is_expired_should_return_401(app, create_user_and_decode):
    client = app.test_client()

    user = await create_user_and_decode()

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

    token = create_jwt(username=str(uuid.uuid4()))

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
