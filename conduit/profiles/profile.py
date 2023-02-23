from dataclasses import dataclass
from typing import Optional


@dataclass
class Profile:
    user_id: str
    username: str
    bio: Optional[str]
    image: Optional[str]
    following: bool
