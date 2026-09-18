from pydantic import BaseModel


class CheckPolicyRequest(BaseModel):
    policy_name: str = ""
    action: str = ""
    context: dict[str, str] = {}
    arguments_json: str = ""
