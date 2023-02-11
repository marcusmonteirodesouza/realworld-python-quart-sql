from dataclasses import dataclass
from typing import Optional


@dataclass
class UserResponseUser:
    email: str
    token: str
    username: str
    bio: Optional[str]
    image: Optional[str]


@dataclass
class UserResponse:
    user: UserResponseUser
