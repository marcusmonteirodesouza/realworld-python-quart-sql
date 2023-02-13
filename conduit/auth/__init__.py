from quart import current_app, Request
from quart_jwt_extended import (
    jwt_required,
    jwt_optional,
    get_jwt_identity,
    verify_jwt_in_request,
    create_access_token as _create_access_token,
)
from ..users import User


verify_jwt_in_request


def create_access_token(user: User) -> str:
    return _create_access_token(identity=str(user.username))


def get_jwt_token(request: Request) -> str:
    header_value = request.headers.get(current_app.config["JWT_HEADER_NAME"])
    token = header_value.split(sep=current_app.config.get("JWT_HEADER_TYPE"))[1].strip()
    return token
