from pydantic import BaseModel
from typing import List

from gogi.models.llm.llm_message import LLMMessage

class AddMessagesToLLMSessionRequest(BaseModel):
    session_id: str 
    messages: List[LLMMessage]