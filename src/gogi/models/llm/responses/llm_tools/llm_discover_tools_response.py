from pydantic import BaseModel

from gogi.models.llm.llm_tool_service_definition import LLMToolServiceDefinition


class LLMDiscoverToolsResponse(BaseModel):
    tools: list[LLMToolServiceDefinition] = []
    relevance_scores: dict[str, float] = {}
