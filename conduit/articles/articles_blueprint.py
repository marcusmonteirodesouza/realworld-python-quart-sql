from http import HTTPStatus
from quart import Blueprint, current_app
from quart_schema import validate_request, validate_response

from .article_response import (
    ArticleResponse,
    ArticleResponseArticle,
    ArticleResponseArticleAuthorProfile,
)
from .create_article_request import CreateArticleRequest
from ..auth import jwt_required, jwt_optional, get_jwt_identity
from ..exceptions import UnauthorizedException

articles_blueprint = Blueprint("articles", __name__)


@articles_blueprint.post(rule="/articles")
@jwt_required
@validate_request(model_class=CreateArticleRequest)
@validate_response(model_class=ArticleResponse, status_code=HTTPStatus.CREATED)
async def create_article(data: CreateArticleRequest) -> (ArticleResponse, int):
    author_username = get_jwt_identity()

    author = await current_app.users_service.get_user_by_username(
        username=author_username
    )

    if not author:
        raise UnauthorizedException(f"author {author_username} not found")

    current_app.logger.info(
        f"received create article request. author_id: {author.id}, data: {data}"
    )

    article = await current_app.articles_service.create_article(
        author_id=author.id,
        title=data.article.title,
        description=data.article.description,
        body=data.article.body,
        tags=data.article.tag_list,
    )

    return (
        ArticleResponse(
            ArticleResponseArticle(
                slug=article.slug,
                title=article.title,
                description=article.description,
                body=article.body,
                tag_list=article.tags,
                created_at=article.created_at,
                updated_at=article.updated_at,
                favorited=False,
                favorites_count=article.favorites_count,
                author=ArticleResponseArticleAuthorProfile(
                    username=author.username,
                    bio=author.bio,
                    image=author.image,
                    following=False,
                ),
            )
        ),
        HTTPStatus.CREATED,
    )


@articles_blueprint.get(rule="/articles/<slug>")
@jwt_optional
@validate_response(model_class=ArticleResponse)
async def get_article(slug: str) -> (ArticleResponse, int):
    article = await current_app.articles_service.get_article_by_slug(slug=slug)

    username = get_jwt_identity()

    if username:
        user = await current_app.users_service.get_user_by_username(username=username)

        if not user:
            raise UnauthorizedException(f"user {username} not found")

        is_favorite = await current_app.articles_service.is_favorite(
            article_id=article.id, user_id=user.id
        )

        author_profile = await current_app.profiles_service.get_profile_by_user_id(
            user_id=article.author_id, follower_id=user.id
        )
    else:
        is_favorite = False

        author_profile = await current_app.profiles_service.get_profile_by_user_id(
            user_id=article.author_id
        )

    return (
        ArticleResponse(
            ArticleResponseArticle(
                slug=article.slug,
                title=article.title,
                description=article.description,
                body=article.body,
                tag_list=article.tags,
                created_at=article.created_at,
                updated_at=article.updated_at,
                favorited=is_favorite,
                favorites_count=article.favorites_count,
                author=ArticleResponseArticleAuthorProfile(
                    username=author_profile.username,
                    bio=author_profile.bio,
                    image=author_profile.image,
                    following=author_profile.following,
                ),
            )
        ),
    )


@articles_blueprint.post(rule="/articles/<slug>/favorite")
@jwt_required
@validate_response(model_class=ArticleResponse)
async def favorite_article(slug: str) -> (ArticleResponse, int):
    author_username = get_jwt_identity()

    user = await current_app.users_service.get_user_by_username(
        username=author_username
    )

    if not user:
        raise UnauthorizedException(f"user {author_username} not found")

    current_app.logger.info(
        f"received favorite article request. user_id: {user.id}, slug: {slug}"
    )

    await current_app.articles_service.favorite_article_by_slug(
        slug=slug, user_id=user.id
    )

    article = await current_app.articles_service.get_article_by_slug(slug=slug)

    author_profile = await current_app.profiles_service.get_profile_by_user_id(
        user_id=article.author_id, follower_id=user.id
    )

    return (
        ArticleResponse(
            ArticleResponseArticle(
                slug=article.slug,
                title=article.title,
                description=article.description,
                body=article.body,
                tag_list=article.tags,
                created_at=article.created_at,
                updated_at=article.updated_at,
                favorited=True,
                favorites_count=article.favorites_count,
                author=ArticleResponseArticleAuthorProfile(
                    username=author_profile.username,
                    bio=author_profile.bio,
                    image=author_profile.image,
                    following=author_profile.following,
                ),
            )
        ),
    )
