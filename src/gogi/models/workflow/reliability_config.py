from pydantic import BaseModel


class ReliabilityConfig(BaseModel):
    timeout_seconds: int = 0
    max_retries: int = 0
