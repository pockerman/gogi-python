from pydantic import BaseModel


class CreateLLMSessionRequest(BaseModel):
    user_id: str
    session_id: str | None = None
