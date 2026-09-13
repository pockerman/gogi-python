from typing import Dict

from pydantic import BaseModel


class CheckPolicyRequest(BaseModel):
    policy_name: str = ""
    action: str = ""
    context: Dict[str, str] = {}
    arguments_json: str = ""
