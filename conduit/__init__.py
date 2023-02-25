import psycopg
from quart import Quart, Blueprint
from quart_jwt_extended import JWTManager
from quart_schema import QuartSchema
from .users import UsersService, users_blueprint
from .profiles import ProfilesService, profiles_blueprint
from .articles import ArticlesService, articles_blueprint
from .error_handlers import add_error_handlers, add_jwt_manager_error_loaders
from .config import config

app = Quart(__name__)

jwt_manager = JWTManager(app=app)

QuartSchema(
    app=app,
    convert_casing=True,
    openapi_path=None,
    redoc_ui_path=None,
    swagger_ui_path=None,
)

app.config.from_object(config)

add_jwt_manager_error_loaders(app=app, jwt_manager=jwt_manager)

add_error_handlers(app=app)


@app.before_serving
async def startup():
    app.aconn = await psycopg.AsyncConnection.connect(app.config["DATABASE_URI"])

    users_service = UsersService(aconn=app.aconn)
    profiles_service = ProfilesService(aconn=app.aconn, users_service=users_service)
    articles_service = ArticlesService(
        aconn=app.aconn, profiles_service=profiles_service
    )

    app.users_service = users_service
    app.profiles_service = profiles_service
    app.articles_service = articles_service

    app.register_blueprint(blueprint=users_blueprint)
    app.register_blueprint(blueprint=profiles_blueprint)
    app.register_blueprint(blueprint=articles_blueprint)


@app.after_serving
async def shutdown():
    await app.aconn.close()
