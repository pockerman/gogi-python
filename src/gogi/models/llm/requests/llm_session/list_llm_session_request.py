from pydantic import BaseModel, Field


class ListLLMSessionsRequest(BaseModel):
    user_id: str
    # the most sessions to return, most recently active first; 0 means all
    limit: int = Field(default=0, ge=0)
    offset: int = Field(default=0, ge=0)
