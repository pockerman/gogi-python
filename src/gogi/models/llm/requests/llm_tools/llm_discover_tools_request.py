from typing import List

from pydantic import BaseModel


class LLMDiscoverToolsRequest(BaseModel):
    namespace: str = ""
    capabilities: List[str] = []
    tags: List[str] = []
    read_only: bool = False
    version_constraint: str = ""
