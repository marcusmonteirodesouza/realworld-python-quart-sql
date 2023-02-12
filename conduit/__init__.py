import psycopg
from quart import Quart
from quart_jwt_extended import JWTManager
from quart_schema import QuartSchema
from .users import UsersService, users_blueprint
from .error_handlers import add_error_handlers, add_jwt_manager_error_loaders
from .config import config

app = Quart(__name__)

jwt_manager = JWTManager(app=app)

QuartSchema(app=app, convert_casing=True)

app.config.from_object(config)

add_jwt_manager_error_loaders(app=app, jwt_manager=jwt_manager)

add_error_handlers(app=app)


@app.before_serving
async def startup():
    app.aconn = await psycopg.AsyncConnection.connect(
        app.config["DATABASE_URI"], autocommit=True
    )

    app.users_service = UsersService(aconn=app.aconn)
    app.register_blueprint(blueprint=users_blueprint)


@app.after_serving
async def shutdown():
    await app.aconn.close()
