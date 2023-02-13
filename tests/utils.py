import datetime
import os
import jwt
from typing import Optional


def create_jwt(
    username: str,
    secret_key: Optional[str] = None,
    expires_seconds: Optional[int] = None,
):
    if not secret_key:
        secret_key = os.environ["SECRET_KEY"]

    if not expires_seconds:
        expires_seconds = int(os.environ["JWT_ACCESS_TOKEN_EXPIRES_SECONDS"])

    iat = datetime.datetime.now(tz=datetime.timezone.utc)
    exp = iat + datetime.timedelta(seconds=expires_seconds)

    payload = {"sub": username, "iat": iat, "exp": exp}

    return jwt.encode(payload=payload, key=secret_key)
