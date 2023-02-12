import json
import pytest


@pytest.mark.asyncio
async def test_when_valid_request_should_return_200(app, faker, user):
    client = app.test_client()

    response = await client.get(
        "/user",
        headers={"Authorization": f"Token {user.token}"},
    )

    assert response.status_code == 200

    response_data = await response.json

    current_user = response_data["user"]

    assert current_user["email"] == user.email
    assert current_user["username"] == user.username
    assert current_user["token"] == user.token
    assert current_user["bio"] == user.bio
    assert current_user["image"] == user.image


@pytest.mark.asyncio
async def test_when_authorization_header_is_not_set_should_return_401(app, faker):
    client = app.test_client()

    response = await client.get(
        "/user",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401

    response_data = await response.json

    print(response_data)

    assert response_data["errors"]["body"][0] == "unauthorized"
