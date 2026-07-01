from pydantic import BaseModel, Field
from typing import Literal, Self, Optional, List

from gogi.models.llm.llm_tool_definition import LLMToolCall

class LLMMessage(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: Optional[str] = None
    tool_calls: List[LLMToolCall] = Field(default_factory=list)
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    timestamp: int 

class LLMMessageGroup(BaseModel):
    messages: list[LLMMessage]

    @classmethod
    def build(cls, messages: list[dict[str, str]]) -> Self:
        return cls(messages=messages)