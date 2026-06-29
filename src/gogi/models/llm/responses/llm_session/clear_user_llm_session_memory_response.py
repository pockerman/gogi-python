from pydantic import BaseModel


class ClearUserLLMSessionMemoryResponse(BaseModel):
    count: int 