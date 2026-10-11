from typing import Any

from pydantic import BaseModel


class CheckPolicyRequest(BaseModel):
    # the tool_validation, behavioral or human_gate policy to apply
    policy_name: str = ""
    # the action to check, e.g. a tool name
    action: str = ""
    # keys with a meaning to policies: user_id, session_id, turn_id, permissions
    context: dict[str, str] = {}
    # the action's arguments as a JSON object; or give them as a dict in arguments
    arguments_json: str = ""
    arguments: dict[str, Any] | None = None
    # instead of policy_name: applies the application's policies, and those of every application
    application_id: str = ""
