from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateUserParams:
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[str] = None
