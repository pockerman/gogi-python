from datetime import datetime

from pydantic import BaseModel


class LLMSession(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime
    # the last time messages were added
    updated_at: datetime
    message_count: int = 0
    # set by get_or_create_session: whether the call created the session
    created: bool = False
