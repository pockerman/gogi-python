from pydantic import BaseModel


class LLMExecuteToolResponse(BaseModel):
    success: bool
    result_json: str = ""
    error: str = ""
    execution_time_ms: int = 0
