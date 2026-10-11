from pydantic import BaseModel, Field


class ListViolationsRequest(BaseModel):
    # filters; empty matches everything
    policy_name: str = ""
    severity: str = ""
    # only violations recorded at or after this time, in unix millis
    since: int = Field(default=0, ge=0)
    # the most violations to return, newest first; 0 means 100, at most 1000
    limit: int = Field(default=0, ge=0)
