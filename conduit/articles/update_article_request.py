from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UpdateArticleRequestArticle:
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    tag_list: Optional[List[str]] = None


@dataclass
class UpdateArticleRequest:
    article: Optional[UpdateArticleRequestArticle]
