from pydantic import BaseModel, Field

# the most models a request may fall back to
MAX_FALLBACK_MODELS = 5


class LLMRetryConfig(BaseModel):
    """How the platform retries a failed call to a model.

    Only errors that may go away are retried: rate limits, overloaded or failing
    servers, timeouts and network errors. The platform caps every value, so a request
    can lower its defaults but not raise them; None takes the platform's default.
    """

    # how many times a failed call is retried; 0 means it is not retried
    max_retries: int | None = Field(default=None, ge=0)
    # the delay before the first retry; the delay doubles on every retry
    initial_delay_ms: int | None = Field(default=None, ge=0)
    # the longest delay between two retries
    max_delay_ms: int | None = Field(default=None, ge=0)


class LLMFallbackModel(BaseModel):
    """A model to fall back to."""

    provider: str = Field(min_length=1)
    model: str


class LLMFallbackConfig(BaseModel):
    """What the platform does when a call to the model fails, after its retries.

    The models are tried in order until one answers; the response's provider and
    model say which one did. They replace the platform's default models to fall back
    to; if empty, the defaults are used. enabled=False turns falling back off,
    including to the defaults; None means enabled.
    """

    enabled: bool | None = None
    models: list[LLMFallbackModel] = Field(default_factory=list, max_length=MAX_FALLBACK_MODELS)
    retry: LLMRetryConfig | None = None
