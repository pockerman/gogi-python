from pydantic import BaseModel


from gogi.clients.models.llm.llm_function_definition import LLMFunctionDefinition

class LLMToolDefinition(BaseModel):
    tool_type: str
    function: LLMFunctionDefinition

class ToolCallFunction(BaseModel):
    name: str 
    arguments: str 


class LLMToolCall(BaseModel):
    idx: str 
    tool_type: str 
    function: ToolCallFunction
