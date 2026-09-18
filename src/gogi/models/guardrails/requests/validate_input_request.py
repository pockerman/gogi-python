from pydantic import BaseModel


class ValidateInputRequest(BaseModel):
    content: str = ""
    checks: list[str] = []
    context: dict[str, str] = {}
