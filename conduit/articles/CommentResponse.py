import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class CommentResponseAuthorProfile:
    username: str
    following: bool
    bio: Optional[str] = None
    image: Optional[str] = None


@dataclass
class CommentResponseComment:
    id: str
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author: CommentResponseAuthorProfile


@dataclass
class CommentResponse:
    comment: CommentResponseComment
