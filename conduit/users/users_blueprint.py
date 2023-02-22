from http import HTTPStatus
from quart import Blueprint, current_app, request
from quart_schema import validate_request, validate_response
from .login_request import LoginRequest
from .register_user_request import RegisterUserRequest
from .update_user_request import UpdateUserRequest
from .user_response import UserResponse, UserResponseUser
from ..auth import create_access_token, jwt_required, get_jwt_identity, get_jwt_token
from ..exceptions import UnauthorizedException

users_blueprint = Blueprint("users", __name__)


@users_blueprint.post(rule="/users")
@validate_request(model_class=RegisterUserRequest)
@validate_response(model_class=UserResponse, status_code=HTTPStatus.CREATED)
async def register_user(data: RegisterUserRequest) -> (UserResponse, int):
    current_app.logger.info(
        f"received register user request. username: {data.user.username}, email: {data.user.email}"
    )

    user = await current_app.users_service.register_user(
        username=data.user.username,
        email=data.user.email,
        password=data.user.password,
    )

    current_app.logger.info(f"user registered! {user}")

    token = create_access_token(user=user)

    return (
        UserResponse(
            user=UserResponseUser(
                username=user.username,
                email=user.email,
                token=token,
                bio=user.bio,
                image=user.image,
            )
        ),
        HTTPStatus.CREATED,
    )


@users_blueprint.post(rule="/users/login")
@validate_request(model_class=LoginRequest)
@validate_response(model_class=UserResponse)
async def login(data: LoginRequest) -> (UserResponse, int):
    current_app.logger.info(f"received login request. email: {data.user.email}")

    is_correct_password = await current_app.users_service.verify_password_by_email(
        email=data.user.email,
        password=data.user.password,
    )

    if not is_correct_password:
        raise UnauthorizedException(f"incorrect password for email:{data.user.email}")

    user = await current_app.users_service.get_user_by_email(email=data.user.email)

    current_app.logger.info(f"login successful! {user}")

    token = create_access_token(user=user)

    return (
        UserResponse(
            user=UserResponseUser(
                username=user.username,
                email=user.email,
                token=token,
                bio=user.bio,
                image=user.image,
            )
        ),
    )


@users_blueprint.get(rule="/user")
@jwt_required
@validate_response(model_class=UserResponse)
async def get_current_user() -> (UserResponse, int):
    username = get_jwt_identity()

    user = await current_app.users_service.get_user_by_username(username=username)

    if not user:
        raise UnauthorizedException(f"username {username} not found")

    token = get_jwt_token(request=request)

    return (
        UserResponse(
            user=UserResponseUser(
                email=user.email,
                token=token,
                username=user.username,
                bio=user.bio,
                image=user.image,
            )
        ),
    )


@users_blueprint.put(rule="/user")
@jwt_required
@validate_request(model_class=UpdateUserRequest)
@validate_response(model_class=UserResponse)
async def update_user(data: UpdateUserRequest) -> (UserResponse, int):
    username = get_jwt_identity()

    user = await current_app.users_service.get_user_by_username(username=username)

    if not user:
        raise UnauthorizedException(f"username {username} not found")

    current_app.logger.info(
        f"received update user request. id: {user.id}, username: {data.user.username}, email:{data.user.email}, bio: {data.user.bio}, image: {data.user.image}"
    )

    updated_user = await current_app.users_service.update_user(
        user_id=user.id,
        username=data.user.username,
        email=data.user.email,
        password=data.user.password,
        bio=data.user.bio,
        image=data.user.image,
    )

    current_app.logger.info(f"user updated! {updated_user}")

    token = get_jwt_token(request=request)

    return (
        UserResponse(
            user=UserResponseUser(
                username=updated_user.username,
                email=updated_user.email,
                token=token,
                bio=updated_user.bio,
                image=updated_user.image,
            )
        ),
    )
