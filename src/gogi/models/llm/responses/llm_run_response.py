from pydantic import BaseModel

from gogi.models.llm.llm_token_usage import LLMTokenUsage
from gogi.models.llm.llm_tool_definition import LLMToolCall


class LLMRunResponse(BaseModel):
    content: str
    model: str
    provider: str
    finish_reason: str | None = None
    token_usage: LLMTokenUsage | None = None
    tool_calls: list[LLMToolCall] | None = None
