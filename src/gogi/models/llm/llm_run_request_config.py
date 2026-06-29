from pydantic import BaseModel

from typing import Optional, List

class LLMRunRequestConfig(BaseModel):

    model: str 
    provider: str
    temperature: float = 0.0 
    max_tokens: int = 1000
    top_p: float = 1.0
    stop_sequences: Optional[List[str]] = None
    frequency_penalty: Optional[float] = None 
    presence_penalty: Optional[float] = None
    system_prompt_name: Optional[str] = None