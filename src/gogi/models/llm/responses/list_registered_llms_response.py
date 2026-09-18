from pydantic import BaseModel

from gogi.models.llm.registered_llm import RegisteredLLM


class ListRegisteredLLMsResponse(BaseModel):
    models: list[RegisteredLLM]
