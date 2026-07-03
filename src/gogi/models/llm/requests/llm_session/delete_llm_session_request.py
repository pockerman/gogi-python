from pydantic import BaseModel

class DeleteLLMSessionRequest(BaseModel):
    session_id: str