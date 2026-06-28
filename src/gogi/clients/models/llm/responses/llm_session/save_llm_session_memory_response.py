from pydantic import BaseModel


class SaveLLMSessionMemoryResponse(BaseModel):
    success: bool
