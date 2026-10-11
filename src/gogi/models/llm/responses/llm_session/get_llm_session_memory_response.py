from typing import Any

from pydantic import BaseModel, Field

from gogi.models.llm.llm_memory_entry import LLMMemoryEntry


class GetLLMSessionMemoryResponse(BaseModel):
    # key to value; a key saved in several scopes maps to its most recently updated value
    memories: dict[str, Any]
    entries: list[LLMMemoryEntry] = Field(default_factory=list)
