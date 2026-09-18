from datetime import datetime

from pydantic import BaseModel


class LLMRegisterResponse(BaseModel):
    name: str
    status: str
    registered_at: datetime
