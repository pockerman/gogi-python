# Using several LLM providers

In this example we use the `LLMModelsClient` (`platform.llm_clients`) to send the same request to two model
providers, OpenAI and Anthropic, through the Gogi platform. The client code is identical for both providers:
only the `provider` and `model` fields of the request configuration change. The LLMs service in the platform
routes each request to the right provider and maps the provider-specific response back to a common format.

The example also shows how to query the providers and models the platform supports, and how to register your
own model and query its status and capabilities.

## Architecture

```
                         LLMRunRequest(provider, model, messages)
  example_3.py ──────────────────────────────────────────────► Gateway ──► LLMs service
       ▲                                                                       │
       │                                                               LLMProviderRouter
       │                                                                ┌──────┴───────┐
       │    LLMRunResponse / stream of LLMRunStreamChunk                ▼              ▼
       └──────────────────────────────────────────────────────  OpenAI provider  Anthropic provider
                                                                (Chat Completions) (Messages API)
```

| File            | What it does                                                                               |
|-----------------|--------------------------------------------------------------------------------------------|
| `example_3.py`  | Lists the providers and models, runs the same request on OpenAI and Anthropic (blocking and streamed), then registers and queries a custom model |

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`
- The LLMs service started with the API keys of both providers:
  - `OPENAI_API_KEY` for OpenAI
  - `ANTHROPIC_API_KEY` for Anthropic
- Optionally `OPENAI_BASE_URL` / `ANTHROPIC_BASE_URL` to route requests through a gateway or proxy

If a key is missing, the request to that provider fails and the example logs the error and carries on with the
next provider.

## Running the example

```bash
python examples/intro/example_3/example_3.py
```

## Walkthrough

### 1. Providers and models

`platform.llm_clients.providers` returns the providers the platform supports and
`platform.llm_clients.provider_models(provider=...)` the models of each. The client caches this list and
`run()` checks every request against it, so a request for a model that is not in the list raises a
`ValueError` before anything is sent to the platform.

### 2. The request

`build_request()` creates an `LLMRunRequest` with a system prompt and a user question. The same messages are
used for both providers, even though the providers handle system prompts differently:

- OpenAI receives the system message as part of the conversation
- Anthropic's Messages API does not accept `system` messages in the conversation, so the Anthropic provider
  moves them to the request's top-level `system` prompt

Some configuration options do not mean the same thing for every provider:

- **Temperature**: a temperature of `0.0` (the default) is treated as "not set", so the provider's own
  default applies. Newer Anthropic models, such as `claude-opus-5-5`, reject sampling parameters
  (`temperature`, `top_p`) altogether, so only set them for models that accept them.
- **`max_tokens`**: newer Anthropic models think before they answer, and the thinking tokens count towards
  `max_tokens`. A limit that is too low ends the response early with the finish reason `max_tokens`.

### 3. Blocking request

`platform.llm_clients.run(request)` returns an `LLMRunResponse` with the content, the model that answered,
the finish reason, the token usage and any tool calls.

### 4. Streamed request

`platform.llm_clients.run_stream(request)` returns an iterator of `LLMRunStreamChunk`. Every chunk except the
last carries a piece of text in `token`. The final chunk carries no text, only the `finish_reason` and the
`usage` of the whole request.

### 5. Comparing the providers

The response format is common, but some values come straight from the provider:

| Field           | OpenAI                                  | Anthropic                                               |
|-----------------|-----------------------------------------|---------------------------------------------------------|
| `model`         | Dated model version, e.g. `gpt-4o-mini-2024-07-18` | The model ID, e.g. `claude-opus-5-5`              |
| `finish_reason` | `stop`, `length`, `tool_calls`, ...     | `end_turn`, `max_tokens`, `tool_use`, `refusal`, ...    |
| `prompt_tokens` | Prompt tokens                           | Input tokens, including tokens read from or written to the prompt cache |

A `refusal` finish reason means Anthropic's safety classifiers declined the request; the content may then be
empty.

### 6. Managing models

`manage_models()` registers a custom model (`my-model`, served by Ollama on `localhost:5000`) with its
capabilities, then lists the registered models and queries the status and capabilities of the new model.

## Driver code

The complete code of the example, `example_3.py`:

```python
"""This example illustrates the LLMModelClient in gogi using two
model providers side by side: OpenAI and Anthropic.

The same request (a system prompt and a user question) is sent to
both providers, first as a blocking request and then as a streamed one,
so the responses, finish reasons and token usage can be compared.
The example then shows how to

- Query the providers and the models the platform supports
- Register your own model
- Query the registered models, their status and capabilities

See example_3.md for a discussion of the example.
"""

import time

import grpc
from loguru import logger
from rich import print as rich_print
from rich.rule import Rule

from gogi.gogi import Gogi
from gogi.models import (
    GetLLMStatusRequest,
    ListRegisteredLLMsRequest,
    LLMCapabilities,
    LLMMessage,
    LLMModelInfo,
    LLMRegisterRequest,
    LLMRunRequest,
    LLMRunRequestConfig,
)
from gogi.models.llm.requests.list_llms_request import ListLLMsRequest
from gogi.models.llm.requests.llm_capabilities_request import GetLLMCapabilitiesRequest

# the (provider, model) pairs to run the same request against
PROVIDER_MODELS = [
    ("openai", "gpt-4o-mini"),
    ("anthropic", "claude-opus-5-5"),
]

SYSTEM_PROMPT = "You are a history tutor. Answer in at most three short paragraphs."
QUESTION = "Who was Alexander the Great?"


def build_request(provider: str, model: str) -> LLMRunRequest:
    # The temperature is left at its default (0.0), which the platform treats as
    # "not set". Newer Anthropic models such as claude-opus-5-5 reject sampling
    # parameters, so only set it for models that accept it.
    # max_tokens is generous because Anthropic's newer models think before
    # answering and the thinking tokens count towards this limit.
    config = LLMRunRequestConfig(model=model, provider=provider, max_tokens=2000)

    now = int(time.time())
    messages = [
        LLMMessage(role="system", content=SYSTEM_PROMPT, timestamp=now),
        LLMMessage(role="user", content=QUESTION, timestamp=now),
    ]
    return LLMRunRequest(config=config, messages=messages)


def run_blocking(platform: Gogi, request: LLMRunRequest) -> None:
    response = platform.llm_clients.run(request)

    rich_print(f"[bold]Model:[/bold] {response.model}")
    rich_print(f"[bold]Finish reason:[/bold] {response.finish_reason}")
    rich_print(f"[bold]Token usage:[/bold] {response.token_usage}")
    rich_print(response.content)


def run_streamed(platform: Gogi, request: LLMRunRequest) -> None:
    for chunk in platform.llm_clients.run_stream(request):
        if chunk.token:
            print(chunk.token, end="", flush=True)

        # the final chunk carries no token, only the finish reason and usage
        if chunk.finish_reason is not None:
            print()
            rich_print(f"[bold]Finish reason:[/bold] {chunk.finish_reason}")
            rich_print(f"[bold]Token usage:[/bold] {chunk.usage}")


def compare_providers(platform: Gogi) -> None:
    for provider, model in PROVIDER_MODELS:
        request = build_request(provider=provider, model=model)

        try:
            rich_print(Rule(f"{provider} / {model}: blocking request"))
            run_blocking(platform, request)

            rich_print(Rule(f"{provider} / {model}: streamed request"))
            run_streamed(platform, request)
        except (ValueError, grpc.RpcError) as e:
            # e.g. the model is not supported or the provider's API key is not set;
            # report it and carry on with the next provider
            logger.error(f"Request to {provider}/{model} failed: {e}")


def manage_models(platform: Gogi) -> None:
    # We can add a new model
    new_model_registration = LLMRegisterRequest(
        info=LLMModelInfo(
            name="my-model",
            provider="ollama",
            capabilities=LLMCapabilities(
                context_window=5000,
                supports_json_mode=False,
                supports_streaming=False,
                supports_tools=True,
                supports_vision=False,
            ),
        ),
        endpoint="http://localhost:5000",
        health_check="http://localhost:5000/health",
        adapter_type="",
    )
    registration_response = platform.llm_clients.register_llm(new_model_registration)
    rich_print(f"Model registration response {registration_response}")

    # what models are registered
    query_response = platform.llm_clients.list_registered_llms(ListRegisteredLLMsRequest())
    rich_print(f"Registered LLMs response {query_response}")

    # check the status of an LLM model
    query_response = platform.llm_clients.get_llm_status(GetLLMStatusRequest(name="my-model"))
    rich_print(f"LLM status response {query_response}")

    # get the capabilities of a model
    query_response = platform.llm_clients.get_llm_capabilities(GetLLMCapabilitiesRequest(model="my-model"))
    rich_print(f"LLM capabilities response {query_response}")

    query_response = platform.llm_clients.list_llms(ListLLMsRequest())
    rich_print(f"List LLMs response {query_response}")


if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # get the providers the platform supports and the models of each
    providers = platform.llm_clients.providers
    rich_print(f"Platform providers {providers}")

    for provider in providers:
        rich_print(f"{provider} models {platform.llm_clients.provider_models(provider=provider)}")

    # send the same request to OpenAI and Anthropic
    compare_providers(platform)

    rich_print(Rule("Model management"))
    manage_models(platform)
```
