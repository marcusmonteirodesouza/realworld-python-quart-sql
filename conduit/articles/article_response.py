import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class ArticleResponseArticleAuthorProfile:
    username: str
    bio: str
    image: str
    following: bool


@dataclass
class ArticleResponseArticle:
    slug: str
    title: str
    description: str
    body: str
    tag_list: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    favorited: bool
    favorites_count: int
    author: ArticleResponseArticleAuthorProfile


@dataclass
class ArticleResponse:
    article: ArticleResponseArticle
