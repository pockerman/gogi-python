from pydantic import BaseModel


class DeleteWorkflowRequest(BaseModel):
    name: str = ""
