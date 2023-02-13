import datetime
import os
import json
import pytest
import jwt


@pytest.mark.asyncio
async def test_when_valid_request_should_return_200(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "email": user.email,
            "password": user.password,
        }
    }

    response = await client.post(
        "/users/login",
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200

    response_data = await response.json

    logged_user = response_data["user"]

    assert logged_user["email"] == user.email
    assert logged_user["username"] == user.username

    decoded_token = jwt.decode(
        jwt=logged_user["token"], key=os.environ["SECRET_KEY"], algorithms="HS256"
    )
    iat = datetime.datetime.now(tz=datetime.timezone.utc)
    exp = iat + datetime.timedelta(
        seconds=int(os.environ["JWT_ACCESS_TOKEN_EXPIRES_SECONDS"])
    )
    assert decoded_token["sub"] == logged_user["username"]
    assert decoded_token["iss"] == os.environ["JWT_ENCODE_ISSUER"]
    assert decoded_token["iat"] == int(iat.timestamp())
    assert decoded_token["exp"] == int(exp.timestamp())

    assert logged_user["bio"] == user.bio
    assert logged_user["image"] == user.image


@pytest.mark.asyncio
async def test_when_email_is_not_sent_should_return_400(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "password": user.password,
        }
    }

    response = await client.post(
        "/users/login",
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "The browser (or proxy) sent a request that this server could not understand."
    )


@pytest.mark.asyncio
async def test_when_email_is_not_found_should_return_401(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "email": faker.email(),
            "password": user.password,
        }
    }

    response = await client.post(
        "/users/login",
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"


@pytest.mark.asyncio
async def test_when_password_is_not_sent_should_return_400(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "email": user.email,
        }
    }

    response = await client.post(
        "/users/login",
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400

    response_data = await response.json

    assert (
        response_data["errors"]["body"][0]
        == "The browser (or proxy) sent a request that this server could not understand."
    )


@pytest.mark.asyncio
async def test_when_password_is_incorrect_should_return_401(app, faker, user):
    client = app.test_client()

    data = {
        "user": {
            "email": user.email,
            "password": faker.password(),
        }
    }

    response = await client.post(
        "/users/login",
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401

    response_data = await response.json

    assert response_data["errors"]["body"][0] == "unauthorized"
