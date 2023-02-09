import psycopg
from quart import Quart
from quart_schema import QuartSchema
from .users import UsersService, users_blueprint
from .error_handler import ErrorHandler
from .config import config

app = Quart(__name__)

QuartSchema(app=app, convert_casing=True)

app.config.from_object(config)

ErrorHandler(app=app)


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
