from dataclasses import dataclass
from typing import Optional


@dataclass
class UserUser:
    email: str
    token: str
    username: str
    bio: Optional[str]
    image: Optional[str]


@dataclass
class User:
    user: UserUser
