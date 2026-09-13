from typing import Dict, List

from pydantic import BaseModel


class FilterOutputRequest(BaseModel):
    content: str = ""
    filters: List[str] = []
    context: Dict[str, str] = {}
