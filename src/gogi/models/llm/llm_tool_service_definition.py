from pydantic import BaseModel


class LLMToolBehavior(BaseModel):
    is_read_only: bool = False
    is_idempotent: bool = False
    requires_confirmation: bool = False
    typical_latency_ms: int = 0
    side_effects: list[str] = []


class LLMRateLimits(BaseModel):
    requests_per_minute: int = 0
    requests_per_session: int = 0
    daily_limit: int = 0


class LLMCostMetadata(BaseModel):
    estimated_cost_usd: float = 0.0
    billing_category: str = ""


class LLMExecutionLimits(BaseModel):
    timeout_seconds: int = 0
    memory_limit_mb: int = 0
    cpu_limit_millicores: int = 0
    max_response_size_kb: int = 0
    max_retries: int = 0


class LLMToolServiceDefinition(BaseModel):
    name: str
    version: str
    owner: str = ""
    description: str = ""
    parameters_json: str = ""
    returns_json: str = ""
    behavior: LLMToolBehavior | None = None
    rate_limits: LLMRateLimits | None = None
    cost: LLMCostMetadata | None = None
    required_permissions: list[str] = []
    capabilities: list[str] = []
    tags: list[str] = []
    endpoint: str = ""
    credential_ref: str = ""
    execution_limits: LLMExecutionLimits | None = None
    mcp_server_url: str = ""
