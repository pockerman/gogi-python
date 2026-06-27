from pydantic import BaseModel
from typing import Optional

class CreateLLMSessionRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None