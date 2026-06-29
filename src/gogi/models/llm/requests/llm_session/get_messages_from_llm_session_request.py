from pydantic import BaseModel
from typing import Optional

class GetMessagesFromLLMSessionRequest(BaseModel):
    session_id: str
    limit: Optional[int] = None
    offset: Optional[int] = None
    strategy: Optional[str] = None
