import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AuthorProfile:
    username: str
    following: bool
    bio: Optional[str] = None
    image: Optional[str] = None


@dataclass
class Article:
    slug: str
    title: str
    description: str
    body: str
    tag_list: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    favorited: bool
    favorites_count: int
    author: AuthorProfile
