from pydantic import BaseModel


class UpdateJobProgressResponse(BaseModel):
    success: bool = False
