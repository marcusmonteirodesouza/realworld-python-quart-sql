from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: str
    username: str
    email: str
    bio: Optional[str]
    image: Optional[str]
