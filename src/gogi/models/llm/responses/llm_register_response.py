from pydantic import BaseModel
from datetime import datetime



class LLMRegisterResponse(BaseModel):
    name: str 
    status: str
    registered_at: datetime 
