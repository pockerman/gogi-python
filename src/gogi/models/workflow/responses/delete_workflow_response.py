from pydantic import BaseModel


class DeleteWorkflowResponse(BaseModel):
    success: bool = False
