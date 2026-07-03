from pydantic import BaseModel
from typing import Optional

class GetLLMSessionMemoryRequest(BaseModel):
    user_id: str
    key: Optional[str] = None
    session_id: Optional[str] = None
