from pydantic import BaseModel


class GetMessagesFromLLMSessionRequest(BaseModel):
    session_id: str
    limit: int | None = None
    offset: int | None = None
    strategy: str | None = None
