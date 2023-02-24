import psycopg
import shortuuid
from typing import List, Optional
from slugify import slugify
from .article import Article
from .. import ProfilesService
from ..exceptions import NotFoundException


class ArticlesService:
    def __init__(
        self, aconn: psycopg.AsyncConnection, profiles_service: ProfilesService
    ):
        self._aconn = aconn
        self._profiles_service = profiles_service
        self._articles_table = "articles"
        self._tags_table = "tags"
        self._articles_tags_table = "articles_tags"
        self._favorites_table = "favorites"

    async def create_article(
        self,
        author_id: str,
        title: str,
        description: str,
        body: str,
        tags: Optional[List[str]],
    ) -> Article:
        async with self._aconn.cursor() as acur:
            insert_user_query = f"""
                INSERT INTO {self._articles_table} (author_id, slug, title, description, body, tags)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at, updated_at;
            """

            slug = self._slugify_title(title=title)

            tags = self._slugify_tags(tags=tags) if tags else []

            try:
                await acur.execute(
                    insert_user_query, (author_id, slug, title, description, body, tags)
                )
            except Exception as e:
                await self._aconn.rollback()
                raise e

            record = await acur.fetchone()

            article = Article(
                id=record[0],
                author_id=author_id,
                slug=slug,
                title=title,
                description=description,
                body=body,
                tags=tags,
                created_at=record[1],
                updated_at=record[2],
                favorites_count=0,
            )

        await self._aconn.commit()

        return article

    async def get_article_by_id(self, article_id: str) -> Optional[Article]:
        async with self._aconn.cursor() as acur:
            get_article_by_id_query = f"""
                SELECT author_id, slug, title, description, body, tags, created_at, updated_at
                FROM {self._articles_table}
                WHERE id = %s
                AND deleted_at IS NULL;
            """

            await acur.execute(get_article_by_id_query, (article_id,))

            record = await acur.fetchone()

            if not record:
                raise NotFoundException(f"article {article_id} not found")

            favorites_count = await self._get_favorites_count(
                acur=acur, article_id=article_id
            )

            return Article(
                id=article_id,
                author_id=record[0],
                slug=record[1],
                title=record[2],
                description=record[3],
                body=record[4],
                tags=record[5],
                created_at=record[6],
                updated_at=record[7],
                favorites_count=favorites_count,
            )

    async def get_article_by_slug(self, slug: str) -> Optional[Article]:
        async with self._aconn.cursor() as acur:
            get_article_by_slug_query = f"""
                SELECT id, author_id, title, description, body, tags, created_at, updated_at
                FROM {self._articles_table}
                WHERE slug = %s
                AND deleted_at IS NULL;
            """

            await acur.execute(get_article_by_slug_query, (slug,))

            record = await acur.fetchone()

            if not record:
                raise NotFoundException(f"slug {slug} not found")

            article_id = record[0]

            favorites_count = await self._get_favorites_count(
                acur=acur, article_id=article_id
            )

            return Article(
                id=article_id,
                author_id=record[1],
                slug=slug,
                title=record[2],
                description=record[3],
                body=record[4],
                tags=record[5],
                created_at=record[6],
                updated_at=record[7],
                favorites_count=favorites_count,
            )

    async def list_articles(
        self,
        tag: Optional[str] = None,
        author_id: Optional[str] = None,
        articles_favorited_by_user_id: Optional[str] = None,
        authors_followed_by_user_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Article]:
        list_articles_query = f"""
            SELECT id, author_id, slug, title, description, body, tags, created_at, updated_at
            FROM {self._articles_table} a
            WHERE deleted_at IS NULL
        """

        if limit is None:
            limit = 20

        if offset is None:
            offset = 0

        query_params = {"limit": limit, "offset": offset}

        if tag:
            list_articles_query = f"{list_articles_query} AND %(tag)s = ANY (tags)"
            query_params["tag"] = tag

        if author_id:
            list_articles_query = f"{list_articles_query} AND author_id = %(author_id)s"
            query_params["author_id"] = author_id

        if articles_favorited_by_user_id:
            list_articles_query = f"""
                {list_articles_query}
                AND EXISTS (
                    SELECT 1 FROM {self._favorites_table} f
                    WHERE f.article_id = a.id
                    AND user_id = %(articles_favorited_by_user_id)s
                    AND deleted_at IS NULL
                )
            """
            query_params[
                "articles_favorited_by_user_id"
            ] = articles_favorited_by_user_id

        if authors_followed_by_user_id:
            followed_authors = (
                await self._profiles_service.get_followed_profiles_by_user_id(
                    follower_id=authors_followed_by_user_id
                )
            )

            list_articles_query = f"""
                {list_articles_query}
                AND author_id = ANY(%(followed_authors_ids)s)
            """
            query_params["followed_authors_ids"] = [
                author.user_id for author in followed_authors
            ]

        list_articles_query = f"""
            {list_articles_query}
            ORDER BY created_at DESC
            LIMIT %(limit)s
            OFFSET %(offset)s;
        """

        async with self._aconn.cursor() as acur:
            await acur.execute(list_articles_query, query_params)

            records = await acur.fetchall()

            articles = []

            for record in records:
                article_id = record[0]

                favorites_count = await self._get_favorites_count(
                    acur=acur, article_id=article_id
                )

                article = Article(
                    id=article_id,
                    author_id=record[1],
                    slug=record[2],
                    title=record[3],
                    description=record[4],
                    body=record[5],
                    tags=record[6],
                    created_at=record[7],
                    updated_at=record[8],
                    favorites_count=favorites_count,
                )

                articles.append(article)

            return articles

    async def update_article_by_id(
        self,
        article_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        body: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Article:
        article = await self.get_article_by_id(article_id=article_id)

        if not article:
            raise NotFoundException(f"article {article_id} not found")

        initial_update_article_query = f"UPDATE {self._articles_table}"

        update_article_query = initial_update_article_query

        query_params = {"id": article.id}

        if title:
            if update_article_query == initial_update_article_query:
                update_article_query = (
                    f"{update_article_query} SET title = %(title)s, slug = %(slug)s"
                )
            else:
                update_article_query = (
                    f"{update_article_query}, title = %(title)s, slug = %(slug)s"
                )

            query_params["title"] = title
            query_params["slug"] = self._slugify_title(title=title)

        if description:
            if update_article_query == initial_update_article_query:
                update_article_query = (
                    f"{update_article_query} SET description = %(description)s"
                )
            else:
                update_article_query = (
                    f"{update_article_query}, description = %(description)s"
                )

            query_params["description"] = description

        if body:
            if update_article_query == initial_update_article_query:
                update_article_query = f"{update_article_query} SET body = %(body)s"
            else:
                update_article_query = f"{update_article_query}, body = %(body)s"

            query_params["body"] = body

        if tags:
            if update_article_query == initial_update_article_query:
                update_article_query = f"{update_article_query} SET tags = %(tags)s"
            else:
                update_article_query = f"{update_article_query}, tags = %(tags)s"

            query_params["tags"] = self._slugify_tags(tags=tags)

        async with self._aconn.cursor() as acur:
            if update_article_query != initial_update_article_query:
                update_article_query = f"""
                    {update_article_query}, updated_at = current_timestamp
                    WHERE id = %(id)s
                    AND deleted_at IS NULL;
                """

                try:
                    await acur.execute(
                        update_article_query,
                        params=query_params,
                    )
                except Exception as e:
                    await self._aconn.rollback()
                    raise e

        await self._aconn.commit()

        return await self.get_article_by_id(article_id=article.id)

    async def delete_article_by_id(self, article_id: str):
        async with self._aconn.cursor() as acur:
            delete_article_query = f"""
                UPDATE {self._articles_table}
                SET deleted_at = current_timestamp
                WHERE id = %s
                AND deleted_at IS NULL;
            """

            try:
                await acur.execute(delete_article_query, (article_id,))
            except Exception as e:
                await self._aconn.rollback()
                raise e

            if acur.rowcount == 0:
                await self._aconn.rollback()
                raise NotFoundException(f"article {article_id} not found")

        await self._aconn.commit()

    async def get_tags(self) -> List[str]:
        async with self._aconn.cursor() as acur:
            get_tags_query = f"""
                SELECT array_agg(DISTINCT t)
                FROM {self._articles_table}, UNNEST(tags) as t;
            """

            await acur.execute(get_tags_query)

            records = await acur.fetchall()

            return records[0][0]

    async def favorite_article_by_slug(self, slug: str, user_id: str):
        article = await self.get_article_by_slug(slug=slug)

        if not article:
            raise NotFoundException(f"slug {slug} not found")

        async with self._aconn.cursor() as acur:
            favorite_article_query = f"""
                INSERT INTO {self._favorites_table} (article_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT(article_id, user_id) WHERE deleted_at IS NOT NULL
                DO UPDATE SET deleted_at = NULL;
            """

            try:
                await acur.execute(favorite_article_query, (article.id, user_id))
            except Exception as e:
                await self._aconn.rollback()
                raise e

        await self._aconn.commit()

    async def unfavorite_article_by_slug(self, slug: str, user_id: str):
        article = await self.get_article_by_slug(slug=slug)

        if not article:
            raise NotFoundException(f"slug {slug} not found")

        if not await self.is_favorited(article_id=article.id, user_id=user_id):
            return

        async with self._aconn.cursor() as acur:
            unfavorite_article_query = f"""
                UPDATE {self._favorites_table}
                SET deleted_at = current_timestamp
                WHERE article_id = %s
                AND user_id = %s;
            """

            try:
                await acur.execute(unfavorite_article_query, (article.id, user_id))
            except Exception as e:
                await self._aconn.rollback()
                raise e

        await self._aconn.commit()

    async def is_favorited(self, article_id: str, user_id: str) -> bool:
        async with self._aconn.cursor() as acur:
            is_following_query = f"""
                SELECT EXISTS(
                    SELECT 1 FROM {self._favorites_table}
                    WHERE article_id = %s
                    AND user_id = %s
                    AND deleted_at IS NULL
                );
            """

            await acur.execute(is_following_query, (article_id, user_id))

            record = await acur.fetchone()

            return record[0]

    async def _get_favorites_count(self, acur: psycopg.AsyncCursor, article_id) -> int:
        get_favorites_count_query = f"""
            SELECT COUNT(*)
            FROM {self._favorites_table}
            WHERE article_id = %s
            AND deleted_at IS NULL;
        """

        await acur.execute(get_favorites_count_query, (article_id,))

        record = await acur.fetchone()

        return record[0]

    @staticmethod
    def _slugify(string: str) -> str:
        return slugify(string.strip().lower())

    def _slugify_title(self, title: str) -> str:
        return self._slugify(string=f"{title}-{shortuuid.uuid()}")

    def _slugify_tags(self, tags: List[str]) -> List[str]:
        return sorted(list(dict.fromkeys([self._slugify(string=tag) for tag in tags])))
