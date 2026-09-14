from pydantic import BaseModel


class CancelJobRequest(BaseModel):
    job_id: str = ""
