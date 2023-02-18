from quart import Blueprint, current_app
from quart_schema import validate_response
from .profile_response import ProfileResponse, ProfileResponseProfile
from ..auth import jwt_required, jwt_optional, get_jwt_identity
from ..exceptions import UnauthorizedException

profiles_blueprint = Blueprint("profiles", __name__)


@profiles_blueprint.post(rule="/profiles/<username>/follow")
@jwt_required
@validate_response(model_class=ProfileResponse)
async def follow_user(username: str) -> (ProfileResponse, int):
    follower_username = get_jwt_identity()

    follower = await current_app.users_service.get_user_by_username(
        username=follower_username
    )

    if not follower:
        raise UnauthorizedException(f"follower {follower_username} not found")

    current_app.logger.info(
        f"received follow user request. follower_id: {follower.id}, followed_username: {username}"
    )

    await current_app.profiles_service.follow_user_by_username(
        follower_id=follower.id, followed_username=username
    )

    profile = await current_app.profiles_service.get_profile_by_username(
        username=username, follower_id=follower.id
    )

    return ProfileResponse(
        ProfileResponseProfile(
            username=profile.username,
            bio=profile.bio,
            image=profile.image,
            following=profile.following,
        )
    )


@profiles_blueprint.get(rule="/profiles/<username>")
@jwt_optional
@validate_response(model_class=ProfileResponse)
async def get_profile(username: str) -> (ProfileResponse, int):
    follower_id = None

    follower_username = get_jwt_identity()

    if follower_username:
        follower = await current_app.users_service.get_user_by_username(
            username=follower_username
        )

        if not follower:
            raise UnauthorizedException(f"follower {follower_username} not found")

        follower_id = follower.id

    profile = await current_app.profiles_service.get_profile_by_username(
        username=username, follower_id=follower_id
    )

    return ProfileResponse(
        ProfileResponseProfile(
            username=profile.username,
            bio=profile.bio,
            image=profile.image,
            following=profile.following,
        )
    )


@profiles_blueprint.delete(rule="/profiles/<username>/follow")
@jwt_required
@validate_response(model_class=ProfileResponse)
async def unfollow_user(username: str) -> (ProfileResponse, int):
    follower_username = get_jwt_identity()

    follower = await current_app.users_service.get_user_by_username(
        username=follower_username
    )

    if not follower:
        raise UnauthorizedException(f"follower {follower_username} not found")

    current_app.logger.info(
        f"received unfollow user request. follower_id: {follower.id}, followed_username: {username}"
    )

    await current_app.profiles_service.unfollow_user_by_username(
        follower_id=follower.id, followed_username=username
    )

    profile = await current_app.profiles_service.get_profile_by_username(
        username=username, follower_id=follower.id
    )

    return ProfileResponse(
        ProfileResponseProfile(
            username=profile.username,
            bio=profile.bio,
            image=profile.image,
            following=profile.following,
        )
    )
