from pydantic import BaseModel, Field

from gogi.models.llm.llm_message import LLMMessage


class GetMessagesFromLLMSessionResponse(BaseModel):
    # the page of the history, or the assembled context, ready to send to a model
    messages: list[LLMMessage]
    # the number of messages of the session
    total_count: int
    # the strategy applied; it differs from the one asked for when the platform falls back
    strategy: str = "none"
    # the stored messages the context leaves out, or covers with the summary
    omitted_count: int = 0
    summarized_count: int = 0
    summary: str = ""
    estimated_tokens: int = 0
    notes: list[str] = Field(default_factory=list)
