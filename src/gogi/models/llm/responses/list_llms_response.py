from pydantic import BaseModel

from gogi.models.llm.llm_model_info import LLMModelInfo


class ListLLMsResponse(BaseModel):
    models: list[LLMModelInfo] | None
