from pydantic import BaseModel


class TriggeredRule(BaseModel):
    """A rule that triggered during a guardrail evaluation."""

    policy_name: str = ""
    # e.g. prompt_injection, pii_detection, tool_validation, max_per_session, human_gate
    rule_type: str = ""
    # block, redirect, warn, redact, log_only or require_approval
    action: str = ""
    severity: str = ""
    # what triggered, e.g. "credit_card", without repeating the content
    detail: str = ""
    # the policy is in shadow mode: the rule was recorded, not enforced
    shadow: bool = False
