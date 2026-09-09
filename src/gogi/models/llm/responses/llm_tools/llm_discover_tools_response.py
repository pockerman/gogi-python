from typing import Dict, List

from pydantic import BaseModel

from gogi.models.llm.llm_tool_service_definition import LLMToolServiceDefinition


class LLMDiscoverToolsResponse(BaseModel):
    tools: List[LLMToolServiceDefinition] = []
    relevance_scores: Dict[str, float] = {}
