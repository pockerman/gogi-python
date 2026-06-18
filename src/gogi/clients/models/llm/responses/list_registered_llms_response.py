from pydantic import BaseModel
from typing import List

from gogi.clients.models.llm.registered_llm import RegisteredLLM

class ListRegisteredLLMsResponse(BaseModel):
    models: List[RegisteredLLM]
