"""This example illustrates resilient calls to models: the platform retries failed
calls and, if a model keeps failing, falls back to other models.

- Registers a model at an endpoint nothing listens on, so every call to it fails
- Calls it without fallback: the platform retries, then reports the error
- Calls it with a model to fall back to: the response says which model answered
- Streams with fallback: every chunk names its provider
- Turns fallback off for a request, and lowers the platform's retries

See example_9.md for a discussion of the example.
"""

import os
import time

import grpc
from loguru import logger
from rich import print as rich_print
from rich.rule import Rule

from gogi.gogi import Gogi
from gogi.models import (
    LLMCapabilities,
    LLMFallbackConfig,
    LLMFallbackModel,
    LLMMessage,
    LLMModelInfo,
    LLMRegisterRequest,
    LLMRetryConfig,
    LLMRunRequest,
    LLMRunRequestConfig,
)

# the model to fall back to; it must be one the platform can call
FALLBACK_PROVIDER = os.environ.get("GOGI_EXAMPLE_FALLBACK_PROVIDER", "openai")
FALLBACK_MODEL = os.environ.get("GOGI_EXAMPLE_FALLBACK_MODEL", "gpt-4o-mini")

# a model that always fails: nothing listens on port 9 of the model service's host
FAILING_PROVIDER = "unreachable"
FAILING_MODEL = "llama3.2"
FAILING_ENDPOINT = "http://127.0.0.1:9/v1"

QUESTION = "In one sentence, why do distributed systems retry failed calls with backoff?"


def register_failing_model(platform: Gogi) -> None:
    """Registers a model whose endpoint is unreachable. Registering does not call the
    endpoint, so the platform knows the model, but every call to it fails"""
    platform.llm_clients.register_llm(
        LLMRegisterRequest(
            info=LLMModelInfo(
                name=FAILING_MODEL,
                provider=FAILING_PROVIDER,
                capabilities=LLMCapabilities(
                    context_window=128_000,
                    supports_json_mode=False,
                    supports_streaming=True,
                    supports_tools=False,
                    supports_vision=False,
                ),
            ),
            endpoint=FAILING_ENDPOINT,
            health_check="/api/version",
            adapter_type="openai",
        )
    )
    # the client caches the providers, so refresh them to pick up the new one
    platform.llm_clients.get_llm_providers()


def request(fallback: LLMFallbackConfig | None = None) -> LLMRunRequest:
    return LLMRunRequest(
        config=LLMRunRequestConfig(
            provider=FAILING_PROVIDER, model=FAILING_MODEL, max_tokens=200, fallback=fallback
        ),
        messages=[LLMMessage(role="user", content=QUESTION)],
    )


def to_fallback_model(**kwargs) -> LLMFallbackConfig:
    return LLMFallbackConfig(models=[LLMFallbackModel(provider=FALLBACK_PROVIDER, model=FALLBACK_MODEL)], **kwargs)


def without_fallback(platform: Gogi) -> None:
    rich_print(Rule("Without fallback"))

    # unless the operator set default models to fall back to, a failed call is only
    # retried: by default twice, waiting about a second in all
    start = time.monotonic()
    try:
        platform.llm_clients.run(request())
    except grpc.RpcError as e:
        # UNAVAILABLE: the error may go away, so trying again later may help
        rich_print(f"Failed after {time.monotonic() - start:.1f}s with {e.code().name}: {e.details()}")


def with_fallback(platform: Gogi) -> None:
    rich_print(Rule("With fallback"))

    # the failing model is retried, then the model to fall back to answers
    start = time.monotonic()
    response = platform.llm_clients.run(request(to_fallback_model()))
    rich_print(f"Answered after {time.monotonic() - start:.1f}s by {response.provider}/{response.model}")
    rich_print(response.content)


def stream_with_fallback(platform: Gogi) -> None:
    rich_print(Rule("Streaming with fallback"))

    # a stream falls back only until its first chunk; every chunk names its provider
    providers = set()
    for chunk in platform.llm_clients.run_stream(request(to_fallback_model())):
        providers.add(chunk.provider)
        print(chunk.token, end="", flush=True)
    print()
    rich_print(f"Streamed by {providers}")


def fewer_retries_and_no_fallback(platform: Gogi) -> None:
    rich_print(Rule("Fewer retries, fallback off"))

    # a request can lower the platform's retries, not raise them: here it is not retried
    start = time.monotonic()
    response = platform.llm_clients.run(request(to_fallback_model(retry=LLMRetryConfig(max_retries=0))))
    rich_print(
        f"Without retries, answered after {time.monotonic() - start:.1f}s by {response.provider}/{response.model}"
    )

    # enabled=False turns fallback off, even with models to fall back to, or the
    # platform's default ones
    try:
        platform.llm_clients.run(request(to_fallback_model(enabled=False, retry=LLMRetryConfig(max_retries=0))))
    except grpc.RpcError as e:
        rich_print(f"With fallback off, failed with {e.code().name}")


if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    register_failing_model(platform)

    without_fallback(platform)
    with_fallback(platform)
    stream_with_fallback(platform)
    fewer_retries_and_no_fallback(platform)
