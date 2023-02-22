from dataclasses import dataclass
from typing import List
from conduit.articles.article_response import ArticleResponse


@dataclass
class MultipleArticlesResponse:
    articles: List[ArticleResponse]
    articles_count: int
