from pydantic import BaseModel


class FailJobResponse(BaseModel):
    success: bool = False
