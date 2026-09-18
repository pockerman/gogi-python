from pydantic import BaseModel


class LLMRunRequestConfig(BaseModel):
    model: str
    provider: str
    temperature: float = 0.0
    max_tokens: int = 1000
    top_p: float = 1.0
    stop_sequences: list[str] | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    system_prompt_name: str | None = None
