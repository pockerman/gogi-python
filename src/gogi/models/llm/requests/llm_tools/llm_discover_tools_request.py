from pydantic import BaseModel


class LLMDiscoverToolsRequest(BaseModel):
    namespace: str = ""
    capabilities: list[str] = []
    tags: list[str] = []
    read_only: bool = False
    version_constraint: str = ""
