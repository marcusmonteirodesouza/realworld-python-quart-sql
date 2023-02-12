from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    email: str
    token: str
    username: str
    bio: Optional[str]
    image: Optional[str]
    password: str
