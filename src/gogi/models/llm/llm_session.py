from pydantic import BaseModel
from datetime import datetime

class LLMSession(BaseModel):

    session_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
