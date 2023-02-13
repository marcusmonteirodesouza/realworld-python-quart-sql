import dataclasses
import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import List
from quart import Quart, Response
from quart_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException
from .exceptions import AlreadyExistsException, UnauthorizedException


@dataclass
class _ErrorResponseBody:
    body: List[str]


@dataclass
class _ErrorResponse:
    errors: _ErrorResponseBody


def add_jwt_manager_error_loaders(app: Quart, jwt_manager: JWTManager):
    def unauthorized_callback(reason: str) -> Response:
        app.logger.error(reason)

        response = Response(
            response=json.dumps(
                dataclasses.asdict(_ErrorResponse(_ErrorResponseBody(["unauthorized"])))
            ),
            status=HTTPStatus.UNAUTHORIZED,
            headers={"Content-Type": "application/json"},
        )
        return response

    jwt_manager.invalid_token_loader(callback=unauthorized_callback)
    jwt_manager.unauthorized_loader(callback=unauthorized_callback)
    jwt_manager.expired_token_loader(callback=unauthorized_callback)


def add_error_handlers(app: Quart):
    @app.errorhandler(AlreadyExistsException)
    def handle_value_error(e: AlreadyExistsException):
        app.logger.error(e)

        return (
            _ErrorResponse(_ErrorResponseBody([str(e)])),
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    @app.errorhandler(UnauthorizedException)
    def handle_value_error(e: UnauthorizedException):
        app.logger.error(e)

        return (
            _ErrorResponse(_ErrorResponseBody(["unauthorized"])),
            HTTPStatus.UNAUTHORIZED,
        )

    @app.errorhandler(ValueError)
    def handle_value_error(e: ValueError):
        app.logger.error(e)

        return (
            _ErrorResponse(_ErrorResponseBody([str(e)])),
            HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        try:
            app.logger.error(e.validation_error.json())
        except AttributeError:
            app.logger.error(e)

        return _ErrorResponse(_ErrorResponseBody([e.description])), e.code

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        app.logger.error(e)
        return (
            _ErrorResponse(_ErrorResponseBody(["internal server error"])),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
