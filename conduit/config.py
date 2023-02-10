import os


class _Config:
    DATABASE_URI = os.environ["DATABASE_URI"]
    PORT = int(os.environ["PORT"])
    SECRET_KEY = os.environ["SECRET_KEY"]
    JWT_ISSUER = os.environ["JWT_ISSUER"]
    JWT_VALID_FOR_SECONDS = int(os.environ["JWT_VALID_FOR_SECONDS"])
    DEBUG = os.environ.get("DEBUG") or False

    @staticmethod
    def init_app(app):
        pass


config = _Config()
