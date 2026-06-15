from pydantic import BaseModel

from typing import Optional

class LLMTokenUsage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None  
    total_tokens: Optional[int] = None 