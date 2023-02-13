import psycopg
import validators
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from .update_user_params import UpdateUserParams
from .user import User
from ..exceptions import AlreadyExistsException


class UsersService:
    def __init__(self, aconn: psycopg.AsyncConnection):
        self._aconn = aconn
        self._users_table = "users"

    async def register_user(self, username: str, email: str, password: str) -> User:
        self._validate_email(email=email)

        self._validate_password(password=password)

        password_hash = self._generate_password_hash(password=password)

        async with self._aconn.cursor() as acur:
            insert_user_query = f"""
                INSERT INTO {self._users_table} (username, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id;
            """

            try:
                await acur.execute(insert_user_query, (username, email, password_hash))
            except psycopg.errors.UniqueViolation as e:
                if e.diag.constraint_name == f"{self._users_table}_username_key":
                    raise AlreadyExistsException("username is taken")
                elif e.diag.constraint_name == f"{self._users_table}_email_key":
                    raise AlreadyExistsException("email is taken")
                else:
                    raise e

            record = await acur.fetchone()

            user = User(
                id=record[0],
                username=username,
                email=email,
                bio=None,
                image=None,
            )

            return user

    async def get_user_by_id(self, id: str) -> Optional[User]:
        async with self._aconn.cursor() as acur:
            get_user_by_email_query = f"""
                SELECT username, email, bio, image
                FROM {self._users_table}
                WHERE id = %s;
            """

            await acur.execute(get_user_by_email_query, (id,))

            record = await acur.fetchone()

            if not record:
                return

            user = User(
                id=id,
                username=record[0],
                email=record[1],
                bio=record[2],
                image=record[3],
            )

            return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        async with self._aconn.cursor() as acur:
            get_user_by_username_query = f"""
                SELECT id, email, bio, image
                FROM {self._users_table}
                WHERE username = %s;
            """

            await acur.execute(get_user_by_username_query, (username,))

            record = await acur.fetchone()

            if not record:
                return

            user = User(
                id=record[0],
                username=username,
                email=record[1],
                bio=record[2],
                image=record[3],
            )

            return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self._aconn.cursor() as acur:
            get_user_by_email_query = f"""
                SELECT id, username, bio, image
                FROM {self._users_table}
                WHERE email = %s;
            """

            await acur.execute(get_user_by_email_query, (email,))

            record = await acur.fetchone()

            if not record:
                return

            user = User(
                id=record[0],
                username=record[1],
                email=email,
                bio=record[2],
                image=record[3],
            )

            return user

    async def update_user(self, user_id: str, params: UpdateUserParams):
        initial_update_user_query = f"UPDATE {self._users_table}"

        update_user_query = initial_update_user_query

        query_params = {"id": user_id}

        if params.username:
            if update_user_query == initial_update_user_query:
                update_user_query = f"{update_user_query} SET username = %(username)s"
            else:
                update_user_query = f"{update_user_query}, username = %(username)s"

            query_params["username"] = params.username

        if params.email:
            self._validate_email(email=params.email)

            if update_user_query == initial_update_user_query:
                update_user_query = f"{update_user_query} SET email = %(email)s"
            else:
                update_user_query = f"{update_user_query}, email = %(email)s"

            query_params["email"] = params.email

        if params.password:
            self._validate_password(params.password)

            if update_user_query == initial_update_user_query:
                update_user_query = (
                    f"{update_user_query} SET password_hash = %(password_hash)s"
                )
            else:
                update_user_query = (
                    f"{update_user_query}, password_hash = %(password_hash)s"
                )

            query_params["password_hash"] = self._generate_password_hash(
                password=params.password
            )

        if params.bio:
            if update_user_query == initial_update_user_query:
                update_user_query = f"{update_user_query} SET bio = %(bio)s"
            else:
                update_user_query = f"{update_user_query}, bio = %(bio)s"

            query_params["bio"] = params.bio

        if params.image:
            self._validate_image(image=params.image)

            if update_user_query == initial_update_user_query:
                update_user_query = f"{update_user_query} SET image = %(image)s"
            else:
                update_user_query = f"{update_user_query}, image = %(image)s"

            query_params["image"] = params.image

        if update_user_query != initial_update_user_query:
            update_user_query = f"""
            {update_user_query}, updated_at = current_timestamp
            WHERE id = %(id)s
            RETURNING username, email, bio, image
            """

            async with self._aconn.cursor() as acur:
                try:
                    await acur.execute(
                        update_user_query,
                        params=query_params,
                    )
                except psycopg.errors.UniqueViolation as e:
                    if e.diag.constraint_name == f"{self._users_table}_username_key":
                        raise AlreadyExistsException("username is taken")
                    elif e.diag.constraint_name == f"{self._users_table}_email_key":
                        raise AlreadyExistsException("email is taken")
                    else:
                        raise e

                record = await acur.fetchone()

                user = User(
                    id=user_id,
                    username=record[0],
                    email=record[1],
                    bio=record[2],
                    image=record[3],
                )

                return user
        else:
            return await self.get_user_by_id(id=user_id)

    async def verify_password_by_email(self, email: str, password: str) -> bool:
        async with self._aconn.cursor() as acur:
            get_password_hash_query = f"""
                SELECT password_hash FROM {self._users_table}
                WHERE email = %s;
            """

            await acur.execute(get_password_hash_query, (email,))

            record = await acur.fetchone()

            if not record:
                return False

            password_hash = record[0]

            return check_password_hash(pwhash=password_hash, password=password)

    @staticmethod
    def _validate_email(email: str):
        if not validators.email(email):
            raise ValueError(f"invalid email {email}")

    @staticmethod
    def _validate_password(password: str):
        min_password_length = 8
        max_password_length = 64

        if not len(password) >= min_password_length:
            raise ValueError(
                f"password length must be greater than or equal to {min_password_length}"
            )

        if not len(password) <= max_password_length:
            raise ValueError(
                f"password length must be less than or equal to {max_password_length}"
            )

    @staticmethod
    def _validate_image(image: str):
        if not validators.url(image):
            raise ValueError(f"invalid image {image}. It must be a valid url")

    @staticmethod
    def _generate_password_hash(password: str):
        return generate_password_hash(password=password)
