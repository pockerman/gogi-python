from pydantic import BaseModel


class LLMProvider(BaseModel):
    name: str
    models: list[str] | None = None
