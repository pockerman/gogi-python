from pydantic import BaseModel


class UpdateJobProgressRequest(BaseModel):
    job_id: str = ""
    progress_message: str = ""
