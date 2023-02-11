import psycopg
from quart import Quart
from quart_schema import QuartSchema
from .auth import JWTService
from .users import UsersService, users_blueprint
from .error_handlers import add_error_handlers
from .config import config

app = Quart(__name__)

QuartSchema(app=app, convert_casing=True)

app.config.from_object(config)

add_error_handlers(app=app)


@app.before_serving
async def startup():
    app.aconn = await psycopg.AsyncConnection.connect(
        app.config["DATABASE_URI"], autocommit=True
    )

    app.jwt_service = JWTService(
        secret_key=app.config["SECRET_KEY"],
        jwt_issuer=app.config["JWT_ISSUER"],
        jwt_valid_for_seconds=app.config["JWT_VALID_FOR_SECONDS"],
    )

    app.users_service = UsersService(aconn=app.aconn)
    app.register_blueprint(blueprint=users_blueprint)


@app.after_serving
async def shutdown():
    await app.aconn.close()
