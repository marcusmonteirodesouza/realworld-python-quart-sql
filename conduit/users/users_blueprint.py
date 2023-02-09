from http import HTTPStatus
from quart import Blueprint, current_app
from quart_schema import validate_request, validate_response
from .register_user_request import RegisterUserRequest
from .user_response import UserResponse, UserResponseUser


users_blueprint = Blueprint("users", __name__)


@users_blueprint.post(rule="/users")
@validate_request(model_class=RegisterUserRequest)
@validate_response(model_class=UserResponse, status_code=HTTPStatus.CREATED)
async def register_user(data: RegisterUserRequest) -> (UserResponse, int):
    current_app.logger.info(f"received register user request {data}...")

    user = await current_app.users_service.register_user(
        username=data.user.username,
        email=data.user.email,
        password=data.user.password,
    )

    current_app.logger.info(f"user registered! {user}")

    token = "token"

    return (
        UserResponse(
            UserResponseUser(
                email=user.email,
                token=token,
                username=user.username,
                bio=user.bio,
                image=user.image,
            )
        ),
        HTTPStatus.CREATED,
    )
