from typing import Literal, Self

from pydantic import BaseModel, Field

from gogi.models.llm.llm_tool_definition import LLMToolCall


class LLMMessage(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None
    timestamp: int


class LLMMessageGroup(BaseModel):
    messages: list[LLMMessage]

    @classmethod
    def build(cls, messages: list[dict[str, str]]) -> Self:
        return cls(messages=messages)
