from pydantic import BaseModel


class ValidateInputRequest(BaseModel):
    content: str = ""
    # built-in checks, which block what they find: prompt_injection, pii_detection
    checks: list[str] = []
    # keys with a meaning to policies: user_id, session_id, turn_id, permissions
    context: dict[str, str] = {}
    # the input policies to apply
    policy_names: list[str] = []
    # applies the input policies of the application, and those of every application
    application_id: str = ""
