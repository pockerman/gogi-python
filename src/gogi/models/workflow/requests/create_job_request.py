from pydantic import BaseModel


class CreateJobRequest(BaseModel):
    workflow_id: str = ""
    input_json: str = ""
    assigned_endpoint: str = ""
