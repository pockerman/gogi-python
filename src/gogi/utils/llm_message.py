from pydantic import BaseModel
from typing import Literal, Self

class LLMessage(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str 

class LLMMessageGroup(BaseModel):
    messages: list[LLMessage]

    @classmethod
    def build(cls, messages: list[dict[str, str]]) -> Self:
        return cls(messages=messages)