from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UpdateArticleParams:
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    tags: Optional[List[str]] = None
