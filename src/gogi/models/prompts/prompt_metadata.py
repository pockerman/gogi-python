from pydantic import BaseModel 
from typing import Dict

class PromptTestInfo(BaseModel):
    test_set_id: str
    test_set_path: str
    metrics: Dict[str, float]


class PromptParameters(BaseModel):
    temperature: float
    max_tokens: int
    stop_sequences: list[str]
    frequency_penalty: float
    presence_penalty: float


class PromptMetadata(BaseModel):
    author: str
    model: str
    parameters: PromptParameters
    test_info: PromptTestInfo