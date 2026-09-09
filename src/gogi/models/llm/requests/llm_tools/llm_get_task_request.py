from pydantic import BaseModel


class LLMGetTaskRequest(BaseModel):
    task_id: str
