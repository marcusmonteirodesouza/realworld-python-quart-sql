import datetime
from dataclasses import dataclass


@dataclass
class Comment:
    id: str
    article_id: str
    author_id: str
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
