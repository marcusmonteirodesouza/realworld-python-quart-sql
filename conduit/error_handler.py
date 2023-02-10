from dataclasses import dataclass
from http import HTTPStatus
from typing import List
from quart import Quart
from quart_schema import RequestSchemaValidationError


@dataclass
class _ErrorResponseBody:
    body: List[str]


@dataclass
class _ErrorResponse:
    errors: _ErrorResponseBody


def ErrorHandler(app: Quart):
    @app.errorhandler(RequestSchemaValidationError)
    def handle_request_validation_error(e: RequestSchemaValidationError):
        return (
            _ErrorResponse(_ErrorResponseBody([e.validation_error.json()])),
            HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(ValueError)
    def handle_value_error(e: ValueError):
        return (
            _ErrorResponse(_ErrorResponseBody([str(e)])),
            HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        app.logger.error(e)
        return (
            _ErrorResponse(_ErrorResponseBody(["internal server error"])),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
