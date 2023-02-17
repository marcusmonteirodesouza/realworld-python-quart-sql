import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class Article:
    id: str
    author_id: str
    slug: str
    title: str
    description: str
    body: str
    tags: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    favorites_count: int
