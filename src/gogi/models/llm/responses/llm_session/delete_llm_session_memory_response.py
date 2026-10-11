from pydantic import BaseModel


class DeleteLLMSessionMemoryResponse(BaseModel):
    success: bool
    # the number of memories deleted
    count: int = 0
