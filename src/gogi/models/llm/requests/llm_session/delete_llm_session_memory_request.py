from pydantic import BaseModel
from typing import Optional

class DeleteLLMSessionMemoryRequest(BaseModel):
    user_id: str
    key: str
    session_id: Optional[str] = None