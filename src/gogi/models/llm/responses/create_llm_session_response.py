from pydantic import BaseModel


class CreateLLMSessionResponse(BaseModel):
    user_id: str
    session_id: str | None = None
