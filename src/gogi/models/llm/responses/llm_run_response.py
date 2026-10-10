from pydantic import BaseModel

from gogi.models.llm.llm_message import LLMMessage
from gogi.models.llm.llm_token_usage import LLMTokenUsage
from gogi.models.llm.llm_tool_definition import LLMToolCall


class LLMRunResponse(BaseModel):
    content: str
    model: str
    provider: str
    finish_reason: str | None = None
    token_usage: LLMTokenUsage | None = None
    tool_calls: list[LLMToolCall] | None = None

    def to_message(self) -> LLMMessage:
        """The model's answer as the assistant message to add to the conversation.

        If the model called tools, the message has the calls; add it to the conversation
        before the results of the calls.
        """
        return LLMMessage(role="assistant", content=self.content or None, tool_calls=self.tool_calls or [])
