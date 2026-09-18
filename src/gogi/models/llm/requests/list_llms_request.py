from pydantic import BaseModel


class ListLLMsRequest(BaseModel):
    owner: str | None = None
