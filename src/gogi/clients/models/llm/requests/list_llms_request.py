from pydantic import BaseModel
from typing import Optional

class ListLLMsRequest(BaseModel):
    owner: Optional[str] = None