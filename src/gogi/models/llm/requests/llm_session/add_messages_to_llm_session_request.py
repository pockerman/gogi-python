from pydantic import BaseModel

from gogi.models.llm.llm_message import LLMMessage


class AddMessagesToLLMSessionRequest(BaseModel):
    session_id: str
    messages: list[LLMMessage]
