from dataclasses import dataclass
from typing import Optional


@dataclass
class FeedArticlesQueryArgs:
    limit: Optional[int] = None
    offset: Optional[int] = None
