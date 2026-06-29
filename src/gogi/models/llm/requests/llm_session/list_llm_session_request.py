from pydantic import BaseModel


class ListLLMSessionsRequest(BaseModel):
    user_id: str