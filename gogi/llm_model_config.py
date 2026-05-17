from pydantic import BaseModel
from typing import Optional


class LLMModelConfig(BaseModel):
    model: str 
    provider: str
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: Optional[int] = None  