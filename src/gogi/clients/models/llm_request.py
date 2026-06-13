from pydantic import BaseModel
from typing import List, Optional


from gogi.clients.models.llm_message import LLMessage
from gogi.clients.models.llm_tool_definition import LLMToolDefinition
from gogi.clients.models.llm_response_format import LLMRespnseFormat
from gogi.clients.models.llm_run_request_config import LLMRunRequestConfig

class LLMRequest(BaseModel):
    config: LLMRunRequestConfig
    messages: List[LLMessage]
    tools: Optional[List[LLMToolDefinition]]
    response_format: Optional[LLMRespnseFormat]