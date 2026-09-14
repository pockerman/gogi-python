from pydantic import BaseModel


class CompleteJobRequest(BaseModel):
    job_id: str = ""
    result_json: str = ""
