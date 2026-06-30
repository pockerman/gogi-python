from pydantic import BaseModel
from typing import List


from gogi.models.llm.llm_session import LLMSession

class GetMessagesFromLLMSessionResponse(BaseModel):
    messages: List[LLMSession]
    total_count: int