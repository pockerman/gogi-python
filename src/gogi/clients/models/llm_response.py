from pydantic import BaseModel 
from typing import List, Optional

from gogi.clients.models.llm_token_usage import LLMTokenUsage
from gogi.clients.models.llm_tool_definition import LLMToolCall

class LLMResponse(BaseModel):
    content: str 
    model: str 
    provider: str 
    finish_reason: str
    token_usage: LLMTokenUsage
    tool_calls: Optional[List[LLMToolCall]] = None
