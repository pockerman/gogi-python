from pydantic import BaseModel


class SaveLLMSessionMemoryRequest(BaseModel):
    user_id: str
    key: str
    value: str
    session_id: str | None = None
