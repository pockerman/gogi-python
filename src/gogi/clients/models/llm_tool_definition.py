from pydantic import BaseModel


from gogi.clients.models.llm_function_definition import LLMFunctionDefinition

class LLMToolDefinition(BaseModel):
    tool_type: str
    function: LLMFunctionDefinition