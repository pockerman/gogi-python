from pydantic import BaseModel

class DeleteLLMSessionResponse(BaseModel):
    success: bool