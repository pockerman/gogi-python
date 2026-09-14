from pydantic import BaseModel


class UpdateWorkflowResponse(BaseModel):
    version: int = 0
