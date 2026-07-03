from pydantic import BaseModel
from typing import List


class AddMMessagesToLLMSessionResponse(BaseModel):
    success: bool
    message_count: int