from pydantic import BaseModel

from gogi.models.llm.llm_message import LLMMessage
from gogi.models.llm.llm_response_format import LLMRespnseFormat
from gogi.models.llm.llm_run_request_config import LLMRunRequestConfig
from gogi.models.llm.llm_tool_definition import LLMToolDefinition


class LLMRunRequest(BaseModel):
    config: LLMRunRequestConfig
    messages: list[LLMMessage]
    tools: list[LLMToolDefinition] | None = None
    response_format: LLMRespnseFormat | None = None
