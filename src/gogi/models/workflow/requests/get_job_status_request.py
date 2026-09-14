from pydantic import BaseModel


class GetJobStatusRequest(BaseModel):
    job_id: str = ""
