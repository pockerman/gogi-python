from pydantic import BaseModel

from gogi.models.llm.llm_message import LLMMessage


class GetMessagesFromLLMSessionResponse(BaseModel):
    messages: list[LLMMessage]
    total_count: int
