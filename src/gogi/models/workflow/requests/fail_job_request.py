from pydantic import BaseModel


class FailJobRequest(BaseModel):
    job_id: str = ""
    error: str = ""
