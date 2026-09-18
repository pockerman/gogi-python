from datetime import datetime

from pydantic import BaseModel


class LLMSession(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
