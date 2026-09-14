from pydantic import BaseModel

from gogi.models.workflow.scaling_config import ScalingConfig
from gogi.models.workflow.resource_config import ResourceConfig
from gogi.models.workflow.reliability_config import ReliabilityConfig


class WorkflowSpec(BaseModel):
    name: str = ""
    api_path: str = ""
    container_image: str = ""
    response_mode: str = ""
    scaling: ScalingConfig = ScalingConfig()
    resources: ResourceConfig = ResourceConfig()
    reliability: ReliabilityConfig = ReliabilityConfig()
    version: int = 0
