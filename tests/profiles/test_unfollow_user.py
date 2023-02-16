import pytest
import secrets
import uuid
from ..utils import create_jwt


def make_unfollow_user_url(username: str) -> str:
    return f"/profiles/{username}/follow"


@pytest.mark.asyncio
async def test_given_user_is_followed_when_valid_request_and_valid_token_should_return_200(
    app, create_user, follow_user, get_profile
):
    client = app.test_client()

    follower = await create_user()

    followed = await create_user()

    await follow_user(follower_token=follower.token, username=followed.username)

    unfollow_user_response = await client.delete(
        make_unfollow_user_url(username=followed.username),
        headers={"Authorization": f"Token {follower.token}"},
    )

    assert unfollow_user_response.status_code == 200

    unfollow_user_response_data = await unfollow_user_response.json

    profile = unfollow_user_response_data["profile"]

    assert profile["username"] == followed.username
    assert profile["bio"] == followed.bio
    assert profile["image"] == followed.image
    assert not profile["following"]

    get_profile_profile = await get_profile(
        username=followed.username, follower_token=follower.token
    )

    assert not get_profile_profile.following
