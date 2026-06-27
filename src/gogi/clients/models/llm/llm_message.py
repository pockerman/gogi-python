from pydantic import BaseModel
from typing import Literal, Self, Optional

class LLMMessage(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: Optional[str] = None 

class LLMMessageGroup(BaseModel):
    messages: list[LLMMessage]

    @classmethod
    def build(cls, messages: list[dict[str, str]]) -> Self:
        return cls(messages=messages)