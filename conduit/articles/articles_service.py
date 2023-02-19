import psycopg
import shortuuid
from typing import List, Optional
from slugify import slugify
from .article import Article
from .update_article_params import UpdateArticleParams
from ..exceptions import NotFoundException


class ArticlesService:
    def __init__(self, aconn: psycopg.AsyncConnection):
        self._aconn = aconn
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
                INSERT INTO {self._articles_table} (author_id, slug, title, description, body)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at, updated_at;
            """

            slug = self._slugify_title(title=title)

            try:
                await acur.execute(
                    insert_user_query, (author_id, slug, title, description, body)
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
                tags=tags if tags else [],
                created_at=record[1],
                updated_at=record[2],
                favorites_count=0,
            )

            if len(article.tags) > 0:
                article.tags = await self._overwrite_articles_tags(
                    acur=acur, article_id=article.id, tags=tags
                )

        await self._aconn.commit()

        return article

    async def get_article_by_id(self, article_id: str) -> Optional[Article]:
        async with self._aconn.cursor() as acur:
            get_article_by_slug_query = f"""
                SELECT author_id, slug, title, description, body, created_at, updated_at
                FROM {self._articles_table}
                WHERE id = %s;
            """

            await acur.execute(get_article_by_slug_query, (article_id,))

            record = await acur.fetchone()

            if not record:
                raise NotFoundException(f"article {article_id} not found")

            tags = await self._get_articles_tags(acur=acur, article_id=article_id)

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
                tags=tags,
                created_at=record[5],
                updated_at=record[6],
                favorites_count=favorites_count,
            )

    async def get_article_by_slug(self, slug: str) -> Optional[Article]:
        async with self._aconn.cursor() as acur:
            get_article_by_slug_query = f"""
                SELECT id, author_id, title, description, body, created_at, updated_at
                FROM {self._articles_table}
                WHERE slug = %s;
            """

            await acur.execute(get_article_by_slug_query, (slug,))

            record = await acur.fetchone()

            if not record:
                raise NotFoundException(f"slug {slug} not found")

            article_id = record[0]

            tags = await self._get_articles_tags(acur=acur, article_id=article_id)

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
                tags=tags,
                created_at=record[5],
                updated_at=record[6],
                favorites_count=favorites_count,
            )

    async def update_article_by_slug(
        self, slug: str, params: UpdateArticleParams
    ) -> Article:
        article = await self.get_article_by_slug(slug=slug)

        if not article:
            raise NotFoundException(f"slug {slug} not found")

        initial_update_article_query = f"UPDATE {self._articles_table}"

        update_article_query = initial_update_article_query

        query_params = {"id": article.id}

        if params.title:
            if update_article_query == initial_update_article_query:
                update_article_query = (
                    f"{update_article_query} SET title = %(title)s, slug = %(slug)s"
                )
            else:
                update_article_query = (
                    f"{update_article_query}, title = %(title)s, slug = %(slug)s"
                )

            query_params["title"] = params.title
            query_params["slug"] = self._slugify_title(title=params.title)

        if params.description:
            if update_article_query == initial_update_article_query:
                update_article_query = (
                    f"{update_article_query} SET description = %(description)s"
                )
            else:
                update_article_query = (
                    f"{update_article_query}, description = %(description)s"
                )

            query_params["description"] = params.description

        if params.body:
            if update_article_query == initial_update_article_query:
                update_article_query = f"{update_article_query} SET body = %(body)s"
            else:
                update_article_query = f"{update_article_query}, body = %(body)s"

            query_params["body"] = params.body

        async with self._aconn.cursor() as acur:
            if update_article_query != initial_update_article_query:
                update_article_query = f"""
                    {update_article_query}, updated_at = current_timestamp
                    WHERE id = %(id)s;
                """

                try:
                    await acur.execute(
                        update_article_query,
                        params=query_params,
                    )
                except Exception as e:
                    await self._aconn.rollback()
                    raise e

            if params.tags:
                await self._overwrite_articles_tags(
                    acur=acur, article_id=article.id, tags=params.tags
                )

        await self._aconn.commit()

        return await self.get_article_by_id(article_id=article.id)

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

    async def is_favorite(self, article_id: str, user_id: str) -> bool:
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

    async def _get_articles_tags(self, acur: psycopg.AsyncCursor, article_id):
        get_articles_tags_query = f"""
            SELECT t.name
            FROM {self._tags_table} t, {self._articles_tags_table} at
            WHERE t.id = at.tag_id
            AND at.article_id = %s
            ORDER BY t.name;
        """

        await acur.execute(get_articles_tags_query, (article_id,))

        records = await acur.fetchall()

        return [r[0] for r in records]

    async def _overwrite_articles_tags(
        self, acur: psycopg.AsyncCursor, article_id: str, tags: List[str]
    ) -> List[str]:
        delete_articles_tags_query = f"""
            DELETE FROM {self._articles_tags_table}
            WHERE article_id = %s;
        """

        try:
            await acur.execute(delete_articles_tags_query, (article_id,))
        except Exception as e:
            await self._aconn.rollback()
            raise e

        tags = sorted(list(dict.fromkeys([self._slugify(tag) for tag in tags])))

        insert_tags_query = f"""
            INSERT INTO {self._tags_table} (name)
            VALUES (%s)
            ON CONFLICT(name)
            DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """

        insert_tags_params_seq = [(tag,) for tag in tags]

        try:
            await acur.executemany(
                insert_tags_query, params_seq=insert_tags_params_seq, returning=True
            )
        except Exception as e:
            await self._aconn.rollback()
            raise e

        tags_ids = []

        first_record = await acur.fetchone()
        tags_ids.append(first_record[0])
        while acur.nextset():
            record = await acur.fetchone()
            tags_ids.append(record[0])

        insert_articles_tags_query = f"""
            INSERT INTO {self._articles_tags_table} (article_id, tag_id)
            VALUES (%s, %s)
            ON CONFLICT (article_id, tag_id)
            DO NOTHING;
        """

        insert_articles_tags_params_seq = [
            (
                article_id,
                tag_id,
            )
            for tag_id in tags_ids
        ]

        try:
            await acur.executemany(
                insert_articles_tags_query, params_seq=insert_articles_tags_params_seq
            )
        except Exception as e:
            await self._aconn.rollback()
            raise e

        return tags

    async def _get_favorites_count(self, acur: psycopg.AsyncCursor, article_id) -> int:
        get_favorites_count_query = f"""
            SELECT COUNT(*)
            FROM {self._favorites_table}
            WHERE article_id = %s;
        """

        await acur.execute(get_favorites_count_query, (article_id,))

        record = await acur.fetchone()

        return record[0]

    @staticmethod
    def _slugify(string: str) -> str:
        return slugify(string.strip().lower())

    def _slugify_title(self, title: str) -> str:
        return self._slugify(string=f"{title}-{shortuuid.uuid()}")
