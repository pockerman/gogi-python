from pydantic import BaseModel


class ResourceConfig(BaseModel):
    cpu: str = ""
    memory: str = ""
    gpu_type: str = ""
    num_gpus: int = 0
