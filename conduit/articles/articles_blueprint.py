from http import HTTPStatus
from quart import Blueprint, current_app, Response
from quart_schema import validate_request, validate_querystring, validate_response

from .CommentResponse import (
    CommentResponse,
    CommentResponseComment,
    CommentResponseAuthorProfile,
)
from .add_comment_request import AddCommentRequest
from .article_response import (
    ArticleResponse,
    ArticleResponseArticle,
    ArticleResponseArticleAuthorProfile,
)
from .create_article_request import CreateArticleRequest
from .feed_articles_query_args import FeedArticlesQueryArgs
from .list_articles_request_query_args import ListArticlesQueryArgs
from .list_of_tags_response import ListOfTagsResponse
from .multiple_articles_response import (
    MultipleArticlesResponse,
    MultipleArticlesResponseArticle,
    MultipleArticlesResponseAuthorProfile,
)
from .multiple_comments_response import (
    MultipleCommentsResponse,
    MultipleCommentsResponseComment,
    MultipleCommentsResponseAuthorProfile,
)
from .update_article_request import UpdateArticleRequest
from ..auth import jwt_required, jwt_optional, get_jwt_identity
from ..exceptions import UnauthorizedException, NotFoundException

articles_blueprint = Blueprint("articles", __name__, url_prefix="/api")


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
            article=ArticleResponseArticle(
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


@articles_blueprint.get(rule="/articles")
@jwt_optional
@validate_querystring(model_class=ListArticlesQueryArgs)
@validate_response(model_class=MultipleArticlesResponse)
async def list_articles(
    query_args: ListArticlesQueryArgs,
) -> (MultipleArticlesResponse, int):
    username = get_jwt_identity()

    if username:
        current_user = await current_app.users_service.get_user_by_username(
            username=username
        )

        if not current_user:
            raise UnauthorizedException(f"user {username} not found")
    else:
        current_user = None

    if query_args.author:
        author = await current_app.users_service.get_user_by_username(
            username=query_args.author
        )
        if not author:
            raise NotFoundException(f"author {query_args.author} not found")
        author_id = author.id
    else:
        author_id = None

    if query_args.favorited:
        articles_favorited_by_user = (
            await current_app.users_service.get_user_by_username(
                username=query_args.favorited
            )
        )

        if not articles_favorited_by_user:
            raise NotFoundException(
                f"favorited by user {query_args.favorited} not found"
            )
        articles_favorited_by_user_id = articles_favorited_by_user.id
    else:
        articles_favorited_by_user_id = None

    articles = await current_app.articles_service.list_articles(
        tag=query_args.tag,
        author_id=author_id,
        articles_favorited_by_user_id=articles_favorited_by_user_id,
        limit=query_args.limit,
        offset=query_args.offset,
    )

    article_responses = []
    for article in articles:
        if current_user:
            is_favorited_by_current_user = (
                await current_app.articles_service.is_favorited(
                    article_id=article.id, user_id=current_user.id
                )
            )

            author_profile = await current_app.profiles_service.get_profile_by_user_id(
                user_id=article.author_id, follower_id=current_user.id
            )
        else:
            is_favorited_by_current_user = False

            author_profile = await current_app.profiles_service.get_profile_by_user_id(
                user_id=article.author_id
            )

        article_response_article = MultipleArticlesResponseArticle(
            slug=article.slug,
            title=article.title,
            description=article.description,
            body=article.body,
            tag_list=article.tags,
            created_at=article.created_at,
            updated_at=article.updated_at,
            favorited=is_favorited_by_current_user,
            favorites_count=article.favorites_count,
            author=MultipleArticlesResponseAuthorProfile(
                username=author_profile.username,
                bio=author_profile.bio,
                image=author_profile.image,
                following=author_profile.following,
            ),
        )
        article_responses.append(article_response_article)

    return MultipleArticlesResponse(
        articles=article_responses, articles_count=len(article_responses)
    )


@articles_blueprint.get(rule="/articles/feed")
@jwt_required
@validate_querystring(model_class=FeedArticlesQueryArgs)
@validate_response(model_class=MultipleArticlesResponse)
async def feed_articles(
    query_args: ListArticlesQueryArgs,
) -> (MultipleArticlesResponse, int):
    username = get_jwt_identity()

    current_user = await current_app.users_service.get_user_by_username(
        username=username
    )

    if not current_user:
        raise UnauthorizedException(f"user {username} not found")

    articles = await current_app.articles_service.list_articles(
        authors_followed_by_user_id=current_user.id,
        limit=query_args.limit,
        offset=query_args.offset,
    )

    article_responses = []
    for article in articles:
        is_favorited_by_current_user = await current_app.articles_service.is_favorited(
            article_id=article.id, user_id=current_user.id
        )

        author_profile = await current_app.profiles_service.get_profile_by_user_id(
            user_id=article.author_id, follower_id=current_user.id
        )

        article_response_article = MultipleArticlesResponseArticle(
            slug=article.slug,
            title=article.title,
            description=article.description,
            body=article.body,
            tag_list=article.tags,
            created_at=article.created_at,
            updated_at=article.updated_at,
            favorited=is_favorited_by_current_user,
            favorites_count=article.favorites_count,
            author=MultipleArticlesResponseAuthorProfile(
                username=author_profile.username,
                bio=author_profile.bio,
                image=author_profile.image,
                following=author_profile.following,
            ),
        )
        article_responses.append(article_response_article)

    return MultipleArticlesResponse(
        articles=article_responses, articles_count=len(article_responses)
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

        is_favorite = await current_app.articles_service.is_favorited(
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
            article=ArticleResponseArticle(
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


@articles_blueprint.put(rule="/articles/<slug>")
@jwt_required
@validate_request(model_class=UpdateArticleRequest)
@validate_response(model_class=ArticleResponse)
async def update_article(
    slug: str, data: UpdateArticleRequest
) -> (ArticleResponse, int):
    author_username = get_jwt_identity()

    author = await current_app.users_service.get_user_by_username(
        username=author_username
    )

    if not author:
        raise UnauthorizedException(f"author {author_username} not found")

    current_app.logger.info(
        f"received update article request. author_id: {author.id}, slug: {slug}, data: {data}"
    )

    article = await current_app.articles_service.get_article_by_slug(slug=slug)

    if article.author_id != author.id:
        raise UnauthorizedException(
            f"user {author.id} not authorized to modify article {article.id}"
        )

    article = await current_app.articles_service.update_article_by_id(
        article_id=article.id,
        title=data.article.title,
        description=data.article.description,
        body=data.article.body,
        tags=data.article.tag_list,
    )

    return (
        ArticleResponse(
            article=ArticleResponseArticle(
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
    )


@articles_blueprint.delete(rule="/articles/<slug>")
@jwt_required
async def delete_article(slug: str):
    author_username = get_jwt_identity()

    author = await current_app.users_service.get_user_by_username(
        username=author_username
    )

    if not author:
        raise UnauthorizedException(f"author {author_username} not found")

    current_app.logger.info(
        f"received delete article request. author_id: {author.id}, slug: {slug}"
    )

    article = await current_app.articles_service.get_article_by_slug(slug=slug)

    if article.author_id != author.id:
        raise UnauthorizedException(
            f"user {author.id} not authorized to deleted article {article.id}"
        )

    await current_app.articles_service.delete_article_by_id(article_id=article.id)

    return Response(status=HTTPStatus.NO_CONTENT)


@articles_blueprint.get(rule="/tags")
@validate_response(model_class=ListOfTagsResponse)
async def get_tags() -> (ListOfTagsResponse, int):
    tags = await current_app.articles_service.get_tags()

    return ListOfTagsResponse(tags=tags)


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
            article=ArticleResponseArticle(
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


@articles_blueprint.delete(rule="/articles/<slug>/favorite")
@jwt_required
@validate_response(model_class=ArticleResponse)
async def unfavorite_article(slug: str) -> (ArticleResponse, int):
    author_username = get_jwt_identity()

    user = await current_app.users_service.get_user_by_username(
        username=author_username
    )

    if not user:
        raise UnauthorizedException(f"user {author_username} not found")

    current_app.logger.info(
        f"received unfavorite article request. user_id: {user.id}, slug: {slug}"
    )

    await current_app.articles_service.unfavorite_article_by_slug(
        slug=slug, user_id=user.id
    )

    article = await current_app.articles_service.get_article_by_slug(slug=slug)

    author_profile = await current_app.profiles_service.get_profile_by_user_id(
        user_id=article.author_id, follower_id=user.id
    )

    return (
        ArticleResponse(
            article=ArticleResponseArticle(
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
                    username=author_profile.username,
                    bio=author_profile.bio,
                    image=author_profile.image,
                    following=author_profile.following,
                ),
            )
        ),
    )


@articles_blueprint.post(rule="/articles/<slug>/comments")
@jwt_required
@validate_request(model_class=AddCommentRequest)
@validate_response(model_class=CommentResponse, status_code=HTTPStatus.CREATED)
async def add_comment_to_article(
    slug: str, data: AddCommentRequest
) -> (CommentResponse, int):
    author_username = get_jwt_identity()

    author = await current_app.users_service.get_user_by_username(
        username=author_username
    )

    if not author:
        raise UnauthorizedException(f"author {author_username} not found")

    current_app.logger.info(
        f"received add comment to article request. author_id: {author.id}, slug: {slug}, data: {data}"
    )

    comment = await current_app.articles_service.add_comment_to_article_by_slug(
        slug=slug, author_id=author.id, body=data.comment.body
    )

    return (
        CommentResponse(
            comment=CommentResponseComment(
                id=str(comment.id),
                body=comment.body,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                author=CommentResponseAuthorProfile(
                    username=author.username,
                    bio=author.bio,
                    image=author.image,
                    following=False,
                ),
            )
        ),
        HTTPStatus.CREATED,
    )


@articles_blueprint.get(rule="/articles/<slug>/comments")
@jwt_optional
@validate_response(model_class=MultipleCommentsResponse)
async def list_comments_from_article(slug: str) -> (MultipleCommentsResponse, int):
    username = get_jwt_identity()

    if username:
        current_user = await current_app.users_service.get_user_by_username(
            username=username
        )

        if not current_user:
            raise UnauthorizedException(f"user {username} not found")
    else:
        current_user = None

    comments = await current_app.articles_service.list_article_comments_by_slug(
        slug=slug
    )

    comment_responses = []
    for comment in comments:
        if current_user:
            author_profile = await current_app.profiles_service.get_profile_by_user_id(
                user_id=comment.author_id, follower_id=current_user.id
            )
        else:
            author_profile = await current_app.profiles_service.get_profile_by_user_id(
                user_id=comment.author_id
            )

        comment_response_comment = MultipleCommentsResponseComment(
            id=str(comment.id),
            body=comment.body,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            author=MultipleCommentsResponseAuthorProfile(
                username=author_profile.username,
                bio=author_profile.bio,
                image=author_profile.image,
                following=author_profile.following,
            ),
        )
        comment_responses.append(comment_response_comment)

    return MultipleCommentsResponse(comments=comment_responses)


@articles_blueprint.delete(rule="/articles/<slug>/comments/<comment_id>")
@jwt_required
async def delete_comment_from_article(slug: str, comment_id: str):
    author_username = get_jwt_identity()

    author = await current_app.users_service.get_user_by_username(
        username=author_username
    )

    if not author:
        raise UnauthorizedException(f"author {author_username} not found")

    current_app.logger.info(
        f"received delete comment from article request. author_id: {author.id}, slug: {slug}, comment_id: {comment_id}"
    )

    comment = await current_app.articles_service.get_comment_by_id(
        comment_id=comment_id
    )

    if author.id != comment.author_id:
        raise UnauthorizedException(
            f"author {author.id} not authorized to delete comment {comment.id}"
        )

    await current_app.articles_service.delete_comment_from_article_by_slug(
        slug=slug, comment_id=comment_id
    )

    return Response(status=HTTPStatus.NO_CONTENT)
