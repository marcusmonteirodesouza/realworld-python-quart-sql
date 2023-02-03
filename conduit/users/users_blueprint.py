from quart import Blueprint, request, current_app
from .user import User


class UsersBlueprint:
    @property
    def blueprint(self):
        bp = Blueprint("users", __name__)

        @bp.route("/users", methods=["POST"])
        async def register_user():
            request_data = await request.get_json()

            current_app.logger.info(f"received register user request {request_data}...")

            user_data = request_data["user"]

            user = await current_app.users_service.register_user(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
            )

            current_app.logger.info(f"user registered! {user}")

            token = "token"

            return self._to_user_dto(user=user, token=token)

        return bp

    @staticmethod
    def _to_user_dto(user: User, token: str):
        return {
            "user": {
                "email": user.email,
                "token": token,
                "username": user.username,
                "bio": user.bio,
                "image": user.image,
            }
        }
