from pydantic import BaseModel

class LLMStatusResponse(BaseModel):
    name: str
    status: str
    last_checked: str 
    endpoint: str 