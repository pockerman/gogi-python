from pydantic import BaseModel
from typing import List

from gogi.models.llm.llm_session import LLMSession

class ListLLMSessionsResponse(BaseModel):
    sessions: List[LLMSession]