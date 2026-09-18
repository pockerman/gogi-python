from pydantic import BaseModel

from gogi.models.llm.llm_tool_service_definition import LLMRateLimits, LLMToolBehavior


class LLMRegisterMcpServerRequest(BaseModel):
    server_url: str
    namespace: str = ""
    credential_ref: str = ""
    policy_overrides: LLMToolBehavior | None = None
    rate_limit_overrides: LLMRateLimits | None = None
