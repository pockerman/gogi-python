from pydantic import BaseModel

from gogi.models.llm.llm_token_usage import LLMTokenUsage


class LLMRunStreamChunk(BaseModel):
    token: str = ""
    model: str = ""
    finish_reason: str | None = None
    usage: LLMTokenUsage | None = None
