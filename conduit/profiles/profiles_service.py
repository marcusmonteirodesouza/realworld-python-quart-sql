import psycopg
from .profile import Profile
from .. import UsersService
from ..exceptions import AlreadyExistsException, NotFoundException


class ProfilesService:
    def __init__(self, aconn: psycopg.AsyncConnection, users_service: UsersService):
        self._aconn = aconn
        self._users_service = users_service
        self._follows_table = "follows"

    async def follow_user_by_username(
        self, follower_id: str, followee_username: str
    ) -> Profile:
        followee = await self._users_service.get_user_by_username(
            username=followee_username
        )

        if not followee:
            raise NotFoundException(f"username {followee_username} not found")

        async with self._aconn.cursor() as acur:
            follow_user_query = f"""
                INSERT INTO {self._follows_table} (follower_id, followee_id)
                VALUES (%s, %s);
            """

            try:
                await acur.execute(
                    follow_user_query,
                    (
                        follower_id,
                        followee.id,
                    ),
                )
            except psycopg.errors.UniqueViolation as e:
                if e.diag.constraint_name != "follows_follower_id_followee_id_key":
                    raise e

            return Profile(
                username=followee.username,
                bio=followee.bio,
                image=followee.image,
                following=True,
            )
