from pydantic import BaseModel


class GetLLMSessionMemoryRequest(BaseModel):
    user_id: str
    key: str | None = None
    session_id: str | None = None
