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
        raise UnauthorizedException(f"follower {author_username} not found")

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
