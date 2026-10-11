from typing import Any, Literal

from pydantic import BaseModel, Field

PolicyType = Literal["input", "output", "tool_validation", "behavioral", "human_gate"]
PolicyMode = Literal["enforce", "shadow"]


class GuardrailPolicy(BaseModel):
    """A named guardrail policy. The shape of its rules depends on its type; see the
    platform's guardrails service documentation.

    application_id empty means the policy applies to every application. A policy in shadow
    mode is evaluated and recorded, but never blocks or changes anything. revision, source,
    created_at and updated_at are set by the platform.
    """

    name: str
    type: PolicyType
    rules: list[dict[str, Any]] = Field(min_length=1)
    application_id: str = ""
    mode: PolicyMode = "enforce"
    description: str = ""
    # a label for the author's own use, e.g. 1.2.0
    version: str = ""
    revision: int = 0
    # api, or file for policies loaded from the service's policy directory
    source: str = ""
    # unix millis
    created_at: int = 0
    updated_at: int = 0
