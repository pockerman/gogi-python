from pydantic import BaseModel 

from typing import Optional, List

class LLMProvider(BaseModel):
    name: str 
    models: Optional[List[str]] = None