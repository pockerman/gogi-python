from pydantic import BaseModel

from typing import Optional, List

class LLMRunRequestConfig(BaseModel):

    model: str 
    provider: str
    temperature: float 
    max_tokens: int 
    top_p: float 
    stop_sequences: Optional[List[str]]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    system_prompt_name: Optional[str]