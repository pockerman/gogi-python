from pydantic import BaseModel


class GetWorkflowRequest(BaseModel):
    name: str = ""
