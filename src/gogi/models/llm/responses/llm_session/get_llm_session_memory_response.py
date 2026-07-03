from pydantic import BaseModel

class GetLLMSessionMemoryResponse(BaseModel):
    memories: dict[str, str]