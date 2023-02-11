import datetime
import os
import json
import uuid
import pytest
import jwt


@pytest.mark.asyncio
async def test_valid_request_should_return_201(app, faker, user):
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
    exp = iat + datetime.timedelta(seconds=int(os.environ["JWT_VALID_FOR_SECONDS"]))
    uuid.UUID(decoded_token["sub"])
    assert decoded_token["iss"] == os.environ["JWT_ISSUER"]
    assert decoded_token["iat"] == int(iat.timestamp())
    assert decoded_token["exp"] == int(exp.timestamp())

    assert logged_user["bio"] == user.bio
    assert logged_user["image"] == user.image
