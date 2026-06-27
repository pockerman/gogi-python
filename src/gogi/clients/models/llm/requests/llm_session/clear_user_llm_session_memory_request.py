from pydantic import BaseModel

class ClearUserLLMSessionMemoryRequest(BaseModel):
    user_id: str