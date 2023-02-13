from dataclasses import dataclass
from typing import Optional


@dataclass
class ProfileResponseProfile:
    username: str
    bio: Optional[str]
    image: Optional[str]
    following: bool


@dataclass
class ProfileResponse:
    user: ProfileResponseProfile
