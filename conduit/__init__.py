import psycopg
from quart import Quart
from .users import UsersService, UsersBlueprint
from .config import config

app = Quart(__name__)

app.config.from_object(config)


@app.before_serving
async def startup():
    s = "postgres://postgres:postgres@192.168.106.2:5432/conduit"
    app.aconn = await psycopg.AsyncConnection.connect(app.config["DATABASE_URI"])
    app.users_service = UsersService(aconn=app.aconn)
    users_blueprint = UsersBlueprint().blueprint
    app.register_blueprint(blueprint=users_blueprint)


@app.after_serving
async def shutdown():
    await app.aconn.close()
