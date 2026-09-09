from pydantic import BaseModel


class LLMRegisterToolResponse(BaseModel):
    name: str
    version: str
    status: str
