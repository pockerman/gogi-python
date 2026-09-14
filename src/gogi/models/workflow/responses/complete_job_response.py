from pydantic import BaseModel


class CompleteJobResponse(BaseModel):
    success: bool = False
