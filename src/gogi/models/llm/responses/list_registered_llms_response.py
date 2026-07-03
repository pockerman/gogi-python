from pydantic import BaseModel
from typing import List

from gogi.models.llm.registered_llm import RegisteredLLM

class ListRegisteredLLMsResponse(BaseModel):
    models: List[RegisteredLLM]
