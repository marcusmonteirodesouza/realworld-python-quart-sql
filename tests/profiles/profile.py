from dataclasses import dataclass
from typing import Optional


@dataclass
class Profile:
    username: str
    bio: Optional[str]
    image: Optional[str]
    following: bool
