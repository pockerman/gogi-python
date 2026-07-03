from pydantic import BaseModel
from typing import Optional

class SaveLLMSessionMemoryRequest(BaseModel):
    user_id: str
    key: str
    value: str 
    session_id: Optional[str] = None