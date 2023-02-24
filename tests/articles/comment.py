import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CommentAuthorProfile:
    username: str
    following: bool
    bio: Optional[str] = None
    image: Optional[str] = None


@dataclass
class Comment:
    id: str
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author: CommentAuthorProfile
