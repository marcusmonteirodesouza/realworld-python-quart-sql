import json
import pytest


@pytest.mark.asyncio
async def test_valid_request_should_return_201(app, faker):
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
    assert created_user["token"]
    assert created_user["bio"] is None
    assert created_user["image"] is None


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
