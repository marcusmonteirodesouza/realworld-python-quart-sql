import datetime
import os


class _Config:
    DATABASE_URI = os.environ["DATABASE_URI"]
    PORT = int(os.environ["PORT"])
    SECRET_KEY = os.environ["SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(
        seconds=int(os.environ["JWT_ACCESS_TOKEN_EXPIRES_SECONDS"])
    )
    JWT_IDENTITY_CLAIM = "sub"
    JWT_ENCODE_ISSUER = os.environ["JWT_ENCODE_ISSUER"]
    JWT_HEADER_TYPE = "Token"
    DEBUG = os.environ.get("DEBUG") or False

    @staticmethod
    def init_app(app):
        pass


config = _Config()
