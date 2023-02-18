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

    async def get_profile_by_user_id(
        self, user_id: str, follower_id: Optional[str] = None
    ) -> Profile:
        user = await self._users_service.get_user_by_id(id=user_id)

        if not user:
            raise NotFoundException(f"user {user_id} not found")

        profile = Profile(
            username=user.username,
            bio=user.bio,
            image=user.image,
            following=False,
        )

        if follower_id:
            follower = await self._users_service.get_user_by_id(id=follower_id)

            if not follower:
                raise NotFoundException(f"follower {follower_id} not found")

            profile.following = await self._is_following(
                follower_id=follower.id, followed_id=user.id
            )

        return profile

    async def get_profile_by_username(
        self, username: str, follower_id: Optional[str] = None
    ) -> Profile:
        user = await self._users_service.get_user_by_username(username=username)

        if not user:
            raise NotFoundException(f"username {username} not found")

        return await self.get_profile_by_user_id(
            user_id=user.id, follower_id=follower_id
        )

    async def follow_user_by_username(self, follower_id: str, followed_username: str):
        followed = await self._users_service.get_user_by_username(
            username=followed_username
        )

        if not followed:
            raise NotFoundException(f"username {followed_username} not found")

        if follower_id == followed.id:
            raise ValueError("user cannot follow him/herself")

        async with self._aconn.cursor() as acur:
            follow_user_query = f"""
                INSERT INTO {self._follows_table} (follower_id, followed_id)
                VALUES (%(follower_id)s, %(followed_id)s)
                ON CONFLICT(follower_id, followed_id) WHERE deleted_at IS NOT NULL
                DO UPDATE SET deleted_at = NULL;
            """

            try:
                await acur.execute(
                    follow_user_query,
                    {"follower_id": follower_id, "followed_id": followed.id},
                )
            except Exception as e:
                await self._aconn.rollback()
                raise e

        await self._aconn.commit()

    async def unfollow_user_by_username(self, follower_id: str, followed_username: str):
        followed = await self._users_service.get_user_by_username(
            username=followed_username
        )

        if not followed:
            raise NotFoundException(f"username {followed_username} not found")

        async with self._aconn.cursor() as acur:
            unfollow_user_query = f"""
                UPDATE {self._follows_table}
                SET deleted_at = current_timestamp
                WHERE follower_id = %s
                AND followed_id = %s;
            """

            try:
                await acur.execute(
                    unfollow_user_query,
                    (
                        follower_id,
                        followed.id,
                    ),
                )
            except Exception as e:
                await self._aconn.rollback()
                raise e

        await self._aconn.commit()

    async def _is_following(self, follower_id: str, followed_id: str) -> bool:
        async with self._aconn.cursor() as acur:
            is_following_query = f"""
                SELECT EXISTS(
                    SELECT 1 FROM {self._follows_table}
                    WHERE follower_id = %s
                    AND followed_id = %s
                    AND deleted_at IS NULL
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
