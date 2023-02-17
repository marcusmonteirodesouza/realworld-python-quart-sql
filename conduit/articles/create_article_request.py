from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CreateArticleRequestArticle:
    title: str
    description: str
    body: str
    tag_list: Optional[List[str]] = None


@dataclass
class CreateArticleRequest:
    article: CreateArticleRequestArticle
