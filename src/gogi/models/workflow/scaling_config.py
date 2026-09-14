from pydantic import BaseModel


class ScalingConfig(BaseModel):
    min_replicas: int = 0
    max_replicas: int = 0
    target_cpu_percent: int = 0
