from dataclasses import dataclass
from typing import List

from conduit.articles.article_response import ArticleResponseArticle


@dataclass
class MultipleArticlesResponse:
    articles: List[ArticleResponseArticle]
    articles_count: int
