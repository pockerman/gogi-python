from pydantic import BaseModel

class GetLLMStatusRequest(BaseModel):
    name: str
