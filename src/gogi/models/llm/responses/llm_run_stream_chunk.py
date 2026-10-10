from pydantic import BaseModel, Field

from gogi.models.llm.llm_token_usage import LLMTokenUsage
from gogi.models.llm.llm_tool_definition import LLMToolCall


class LLMRunStreamChunk(BaseModel):
    token: str = ""
    model: str = ""
    finish_reason: str | None = None
    usage: LLMTokenUsage | None = None
    # the tools the model calls, complete, in the last chunk
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
