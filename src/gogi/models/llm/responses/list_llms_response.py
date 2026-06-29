from pydantic import BaseModel
from typing import List

from gogi.models.llm.llm_model_info import LLMModelInfo

class ListLLMsResponse(BaseModel):
    models: List[LLMModelInfo] | None 