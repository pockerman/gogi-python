from typing import Literal, Self

from pydantic import BaseModel, Field

from gogi.models.llm.llm_tool_definition import LLMToolCall


class LLMMessage(BaseModel):
    """A message of a conversation with a model.

    An assistant message has the tools the model called, if any, in ``tool_calls``. A ``tool``
    message gives the model the result of one of those calls: ``tool_call_id`` is the id of the
    call and ``content`` its result.
    """

    role: Literal["user", "system", "assistant", "tool"]
    content: str | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None
    timestamp: int = 0

    @classmethod
    def tool_result(cls, tool_call: LLMToolCall, content: str) -> Self:
        """The message that gives the model the result of one of its tool calls."""
        return cls(role="tool", content=content, tool_call_id=tool_call.idx, name=tool_call.function.name)


class LLMMessageGroup(BaseModel):
    messages: list[LLMMessage]

    @classmethod
    def build(cls, messages: list[dict[str, str]]) -> Self:
        return cls(messages=messages)
