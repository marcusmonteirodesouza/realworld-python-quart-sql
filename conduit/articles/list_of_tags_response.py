from dataclasses import dataclass
from typing import List


@dataclass
class ListOfTagsResponse:
    tags: List[str]
