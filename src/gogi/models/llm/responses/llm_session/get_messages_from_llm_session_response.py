from pydantic import BaseModel
from typing import List



from gogi.models.llm.llm_message import LLMMessage

class GetMessagesFromLLMSessionResponse(BaseModel):
    messages: List[LLMMessage]
    total_count: int