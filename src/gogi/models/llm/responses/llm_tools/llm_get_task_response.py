from pydantic import BaseModel


class LLMGetTaskResponse(BaseModel):
    task_id: str
    status: str
    result_json: str = ""
    error: str = ""
