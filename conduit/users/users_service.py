import psycopg
from .user import User


class UsersService:
    def __init__(self, aconn: psycopg.AsyncConnection):
        self._aconn = aconn
        self._users_table = "users"

    async def register_user(self, username: str, email: str, password: str) -> User:
        async with self._aconn.cursor() as acur:
            insert_user_sql = f"""
                INSERT INTO {self._users_table} (username, email, password_hash) 
                VALUES (%s, %s, crypt(%s, gen_salt('bf')))
                RETURNING id; 
            """

            await acur.execute(insert_user_sql, (username, email, password))

            record = await acur.fetchone()

            await self._aconn.commit()

            user = User(
                _id=record[0],
                username=username,
                email=email,
                bio=None,
                image=None,
            )

            return user
