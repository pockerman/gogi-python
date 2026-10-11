from pydantic import BaseModel

from gogi.models.llm.llm_fallback_config import LLMFallbackConfig


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
    # how failed calls are retried and which models are tried if the model fails;
    # None applies the platform's defaults
    fallback: LLMFallbackConfig | None = None
