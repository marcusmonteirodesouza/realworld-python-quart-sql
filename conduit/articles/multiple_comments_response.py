import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MultipleCommentsResponseAuthorProfile:
    username: str
    following: bool
    bio: Optional[str] = None
    image: Optional[str] = None


@dataclass
class MultipleCommentsResponseComment:
    id: str
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author: MultipleCommentsResponseAuthorProfile


@dataclass
class MultipleCommentsResponse:
    comments: List[MultipleCommentsResponseComment]
