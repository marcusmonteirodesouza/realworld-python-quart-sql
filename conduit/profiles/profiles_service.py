import psycopg
from typing import Optional
from .profile import Profile
from .. import UsersService
from ..exceptions import NotFoundException


class ProfilesService:
    def __init__(self, aconn: psycopg.AsyncConnection, users_service: UsersService):
        self._aconn = aconn
        self._users_service = users_service
        self._follows_table = "follows"

    async def get_profile_by_username(
        self, username: str, follower_id: Optional[str] = None
    ) -> Profile:
        followed = await self._users_service.get_user_by_username(username=username)

        if not followed:
            raise NotFoundException(f"user {username} not found")

        profile = Profile(
            username=followed.username,
            bio=followed.bio,
            image=followed.image,
            following=False,
        )

        if follower_id:
            follower = await self._users_service.get_user_by_id(id=follower_id)

            if not follower:
                raise NotFoundException(f"follower {follower_id} not found")

            profile.following = await self._is_following(
                follower_id=follower.id, followed_id=followed.id
            )

        return profile

    async def follow_user_by_username(
        self, follower_id: str, followed_username: str
    ) -> Profile:
        followed = await self._users_service.get_user_by_username(
            username=followed_username
        )

        if not followed:
            raise NotFoundException(f"username {followed_username} not found")

        async with self._aconn.cursor() as acur:
            follow_user_query = f"""
                INSERT INTO {self._follows_table} (follower_id, followed_id)
                VALUES (%s, %s);
            """

            try:
                await acur.execute(
                    follow_user_query,
                    (
                        follower_id,
                        followed.id,
                    ),
                )
            except psycopg.errors.UniqueViolation as e:
                if e.diag.constraint_name != "follows_follower_id_followed_id_key":
                    raise e

            return Profile(
                username=followed.username,
                bio=followed.bio,
                image=followed.image,
                following=True,
            )

    async def unfollow_user_by_username(
        self, follower_id: str, followed_username: str
    ) -> Profile:
        followed = await self._users_service.get_user_by_username(
            username=followed_username
        )

        if not followed:
            raise NotFoundException(f"username {followed_username} not found")

        async with self._aconn.cursor() as acur:
            unfollow_user_query = f"""
                DELETE FROM {self._follows_table}
                WHERE follower_id = %s
                AND followed_id = %s;
            """

            await acur.execute(
                unfollow_user_query,
                (
                    follower_id,
                    followed.id,
                ),
            )

            return Profile(
                username=followed.username,
                bio=followed.bio,
                image=followed.image,
                following=False,
            )

    async def _is_following(self, follower_id: str, followed_id: str) -> bool:
        async with self._aconn.cursor() as acur:
            is_following_query = f"""
                SELECT EXISTS(
                    SELECT 1 FROM {self._follows_table}
                    WHERE follower_id = %s
                    AND followed_id = %s
                );
            """

            await acur.execute(
                is_following_query,
                (
                    follower_id,
                    followed_id,
                ),
            )

            record = await acur.fetchone()

            return record[0]
