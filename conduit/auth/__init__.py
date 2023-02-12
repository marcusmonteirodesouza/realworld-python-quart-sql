from quart_jwt_extended import (
    jwt_required,
    jwt_optional,
    get_jwt_identity,
    create_access_token as _create_access_token,
)
from ..users import User


def create_access_token(user: User) -> str:
    return _create_access_token(identity=str(user.id))
