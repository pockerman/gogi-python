from pydantic import BaseModel

from gogi.models.llm.llm_session import LLMSession


class ListLLMSessionsResponse(BaseModel):
    sessions: list[LLMSession]
