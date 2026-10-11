from pydantic import BaseModel

from gogi.models.guardrails.guardrail_policy import GuardrailPolicy


class AddPolicyResponse(BaseModel):
    policy: GuardrailPolicy
    # rules that are accepted but not enforced yet, e.g. those that need a classifier,
    # and fields the rules do not use
    warnings: list[str] = []
