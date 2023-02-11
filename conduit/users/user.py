from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class User:
    id: UUID
    username: str
    email: str
    bio: Optional[str]
    image: Optional[str]
