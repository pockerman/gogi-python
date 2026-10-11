from typing import Any

from pydantic import BaseModel


class LLMMemoryEntry(BaseModel):
    """A fact saved about a user, for every session or for one."""

    key: str
    # the value, decoded from JSON
    value: Any = None
    # the session the memory belongs to; None for a memory of the user, in every session
    session_id: str | None = None
    # unix millis; pass updated_at as expected_updated_at to save only if the memory did not change since
    created_at: int = 0
    updated_at: int = 0
