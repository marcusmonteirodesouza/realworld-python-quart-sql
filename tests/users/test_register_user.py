import datetime
import json
import os
import uuid
import pytest
import jwt


@pytest.mark.asyncio
async def test_when_valid_request_should_return_201(app, faker):
    client = app.test_client()

    data = {
        "user": {
            "email": faker.email(),
            "password": faker.password(),
            "username": faker.user_name(),
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 201

    response_data = await response.json

    created_user = response_data["user"]

    assert created_user["email"] == data["user"]["email"]
    assert created_user["username"] == data["user"]["username"]

    decoded_token = jwt.decode(
        jwt=created_user["token"], key=os.environ["SECRET_KEY"], algorithms="HS256"
    )
    iat = datetime.datetime.now(tz=datetime.timezone.utc)
    exp = iat + datetime.timedelta(
        seconds=int(os.environ["JWT_ACCESS_TOKEN_EXPIRES_SECONDS"])
    )
    uuid.UUID(decoded_token["sub"])
    assert decoded_token["iss"] == os.environ["JWT_ENCODE_ISSUER"]
    assert decoded_token["iat"] == int(iat.timestamp())
    assert decoded_token["exp"] == int(exp.timestamp())

    assert created_user["bio"] is None
    assert created_user["image"] is None


@pytest.mark.asyncio
async def test_when_username_not_sent_should_return_400(app, faker):
    client = app.test_client()

    data = {
        "user": {
            "email": faker.email(),
            "password": faker.password(),
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "The browser (or proxy) sent a request that this server could not understand."
    )


@pytest.mark.asyncio
async def test_when_username_is_taken_should_return_422(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "email": faker.email(),
            "password": faker.password(),
            "username": user.username,
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"username is taken"


@pytest.mark.asyncio
async def test_when_email_not_sent_should_return_400(app, faker):
    client = app.test_client()

    data = {
        "user": {
            "password": faker.password(),
            "username": faker.user_name(),
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "The browser (or proxy) sent a request that this server could not understand."
    )


@pytest.mark.asyncio
async def test_when_invalid_email_should_return_400(app, faker):
    client = app.test_client()

    data = {
        "user": {
            "email": "an-invalid-email",
            "password": faker.password(),
            "username": faker.user_name(),
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0] == f'invalid email {data["user"]["email"]}'
    )


@pytest.mark.asyncio
async def test_when_email_is_taken_should_return_422(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "email": user.email,
            "password": faker.password(),
            "username": faker.user_name(),
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422

    response_data = await response.json

    assert response_data["errors"]["body"][0] == f"email is taken"


@pytest.mark.asyncio
async def test_when_password_length_less_than_8_should_return_400(app, faker):
    client = app.test_client()

    data = {
        "user": {
            "email": faker.email(),
            "password": faker.password(length=7),
            "username": faker.user_name(),
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "password length must be greater than or equal to 8"
    )


@pytest.mark.asyncio
async def test_when_password_length_greater_than_64_should_return_400(app, faker):
    client = app.test_client()

    data = {
        "user": {
            "email": faker.email(),
            "password": faker.password(length=65),
            "username": faker.user_name(),
        }
    }

    response = await client.post(
        "/users", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "password length must be less than or equal to 64"
    )
