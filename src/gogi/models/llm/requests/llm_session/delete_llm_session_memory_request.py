from pydantic import BaseModel


class DeleteLLMSessionMemoryRequest(BaseModel):
    user_id: str
    key: str
    session_id: str | None = None
