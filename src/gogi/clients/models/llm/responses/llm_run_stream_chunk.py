from pydantic import BaseModel

from typing import Optional

from gogi.clients.models.llm.llm_token_usage import LLMTokenUsage

class LLMRunStreamChunk(BaseModel):
    token: str = ""
    model: str = ""
    finish_reason: Optional[str] = None
    usage: Optional[LLMTokenUsage] = None
