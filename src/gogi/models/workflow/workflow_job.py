from pydantic import BaseModel


class WorkflowJob(BaseModel):
    job_id: str = ""
    workflow_id: str = ""
    status: str = ""
    progress_message: str = ""
    input_json: str = ""
    result_json: str = ""
    error: str = ""
    checkpoint_json: str = ""
    assigned_endpoint: str = ""
    created_at: int = 0
    updated_at: int = 0
