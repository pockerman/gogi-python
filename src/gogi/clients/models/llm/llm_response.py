from pydantic import BaseModel 
from typing import List, Optional

from gogi.clients.models.llm.llm_token_usage import LLMTokenUsage
from gogi.clients.models.llm.llm_tool_definition import LLMToolCall

class LLMResponse(BaseModel):
    content: str 
    model: str 
    provider: str 
    finish_reason: Optional[str] = None
    token_usage: Optional[LLMTokenUsage] = None
    tool_calls: Optional[List[LLMToolCall]] = None
