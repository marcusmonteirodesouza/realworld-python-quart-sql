from dataclasses import dataclass
from typing import Optional


@dataclass
class ListArticlesQueryArgs:
    tag: Optional[str] = None
    author: Optional[str] = None
    favorited: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
