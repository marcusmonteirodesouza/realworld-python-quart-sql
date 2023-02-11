from dataclasses import dataclass
from http import HTTPStatus
from typing import List
from quart import Quart
from werkzeug.exceptions import HTTPException
from .exceptions import AlreadyExistsException, UnauthorizedException


@dataclass
class _ErrorResponseBody:
    body: List[str]


@dataclass
class _ErrorResponse:
    errors: _ErrorResponseBody


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
            HTTPStatus.BAD_REQUEST,
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
