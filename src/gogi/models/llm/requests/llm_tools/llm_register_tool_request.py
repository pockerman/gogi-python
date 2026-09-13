from pydantic import BaseModel

from gogi.models.llm.llm_tool_service_definition import LLMToolServiceDefinition


class LLMRegisterToolRequest(BaseModel):
    tool: LLMToolServiceDefinition
