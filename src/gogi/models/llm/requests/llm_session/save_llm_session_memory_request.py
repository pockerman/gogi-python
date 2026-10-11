from typing import Any

from pydantic import BaseModel, Field


class SaveLLMSessionMemoryRequest(BaseModel):
    user_id: str
    key: str
    # any JSON-serializable value: a string, a number, a list or a dict
    value: Any
    # saves the memory for this session only; None saves it for the user, in every session
    session_id: str | None = None
    # saves only if the memory was last updated at this time (unix millis), or does not exist
    # if 0; otherwise the save fails. None always saves
    expected_updated_at: int | None = Field(default=None, ge=0)
