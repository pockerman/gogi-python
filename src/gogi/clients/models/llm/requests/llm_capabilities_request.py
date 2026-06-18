from pydantic import BaseModel

class GetLLMCapabilitiesRequest(BaseModel):
    model: str