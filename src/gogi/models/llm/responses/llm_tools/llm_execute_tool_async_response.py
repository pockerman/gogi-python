from pydantic import BaseModel


class LLMExecuteToolAsyncResponse(BaseModel):
    task_id: str
    status: str
