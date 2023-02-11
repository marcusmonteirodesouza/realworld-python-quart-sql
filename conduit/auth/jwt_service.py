import datetime
import jwt
from ..users import User


class JWTService:
    def __init__(self, secret_key: str, jwt_issuer: str, jwt_valid_for_seconds: int):
        self._secret_key = secret_key
        self._jwt_issuer = jwt_issuer
        self._jwt_valid_for_seconds = jwt_valid_for_seconds
        self._algorithm = "HS256"

    def encode(self, user: User) -> str:
        iat = datetime.datetime.now(tz=datetime.timezone.utc)
        exp = iat + datetime.timedelta(seconds=self._jwt_valid_for_seconds)

        payload = {
            "sub": str(user.id),
            "iss": self._jwt_issuer,
            "iat": iat,
            "exp": exp,
        }

        return jwt.encode(
            payload=payload, key=self._secret_key, algorithm=self._algorithm
        )
