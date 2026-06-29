from pydantic import BaseModel
from typing import List, Optional


from gogi.models.llm.llm_message import LLMessage
from gogi.models.llm.llm_tool_definition import LLMToolDefinition
from gogi.models.llm.llm_response_format import LLMRespnseFormat
from gogi.models.llm.llm_run_request_config import LLMRunRequestConfig

class LLMRunRequest(BaseModel):
    config: LLMRunRequestConfig
    messages: List[LLMessage]
    tools: Optional[List[LLMToolDefinition]] = None 
    response_format: Optional[LLMRespnseFormat] = None