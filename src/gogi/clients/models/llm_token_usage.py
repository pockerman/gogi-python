from pydantic import BaseModel

class LLMTokenUsage(BaseModel):
    prompt_tokens: int 
    completion_tokens: int 
    total_tokens: int