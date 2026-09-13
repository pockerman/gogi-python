from typing import List

from pydantic import BaseModel


class FilterOutputResponse(BaseModel):
    content: str = ""
    modified: bool = False
    applied_filters: List[str] = []
