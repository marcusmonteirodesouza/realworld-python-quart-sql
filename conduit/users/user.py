import json
from uuid import UUID
from typing import Optional


class User:
    def __init__(
        self,
        _id: UUID,
        username: str,
        email: str,
        bio: Optional[str],
        image: Optional[str],
    ):
        self._id = _id
        self.username = username
        self.email = email
        self.bio = bio
        self.image = image

    def __repr__(self):
        return f"User({str(self._id)}, {self.username}, {self.email}, {self.bio}, {self.image})"

    def __str__(self):
        return json.dumps(
            {
                "_id": str(self._id),
                "username": self.username,
                "email": self.email,
                "bio": self.bio,
                "image": self.image,
            }
        )
