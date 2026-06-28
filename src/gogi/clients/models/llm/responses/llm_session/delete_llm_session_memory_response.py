from pydantic import BaseModel


class DeleteLLMSessionMemoryResponse(BaseModel):
    success: bool