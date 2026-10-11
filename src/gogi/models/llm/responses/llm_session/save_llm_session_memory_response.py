from pydantic import BaseModel

from gogi.models.llm.llm_memory_entry import LLMMemoryEntry


class SaveLLMSessionMemoryResponse(BaseModel):
    success: bool
    entry: LLMMemoryEntry | None = None
