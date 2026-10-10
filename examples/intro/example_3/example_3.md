# Using and adding LLM providers

In this example we use the `LLMModelsClient` (`platform.llm_clients`) to send the same request to two model
providers, OpenAI and Anthropic, through the Gogi platform. The client code is identical for both providers:
only the `provider` and `model` fields of the request configuration change. The LLMs service in the platform
routes each request to the right provider and maps the provider-specific response back to a common format.

The example also shows how to add a new provider, Ollama, by registering a model served by a local Ollama
server, and how to query the new model's status and capabilities.

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

                         LLMRegisterRequest(model, endpoint, health check, adapter, capabilities)
  example_3.py ──────────────────────────────────────────────► Gateway ──► LLMs service (model registry)
                                                                                      ┆ (planned)
                                                                                      ▼
                                                                          Ollama on localhost:11434
```

| File            | What it does                                                                               |
|-----------------|--------------------------------------------------------------------------------------------|
| `example_3.py`  | Lists the providers and models, runs the same request on OpenAI and Anthropic (blocking and streamed), then adds Ollama as a new provider by registering a model it serves |

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`
- The LLMs service started with the API keys of both providers:
  - `OPENAI_API_KEY` for OpenAI
  - `ANTHROPIC_API_KEY` for Anthropic
- Optionally `OPENAI_BASE_URL` / `ANTHROPIC_BASE_URL` to route requests through a gateway or proxy

- For the Ollama part, [Ollama](https://ollama.com) running on `localhost:11434` with the model pulled:

  ```bash
  ollama pull llama3.2
  ```

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

### 6. Adding a new provider: Ollama

The platform supports OpenAI and Anthropic out of the box. Other providers are added by registering a model
they serve. `add_ollama_provider()` registers `llama3.2`, served by a local Ollama server, with an
`LLMRegisterRequest`:

| Field          | Value in the example                   | Meaning                                              |
|----------------|----------------------------------------|------------------------------------------------------|
| `info.name`    | `llama3.2`                             | The model name used in requests                      |
| `info.provider`| `ollama`                               | The provider the model belongs to                    |
| `info.capabilities` | 128K context, tools, streaming, JSON mode, no vision | What the model can do. Clients can query it before choosing a model |
| `endpoint`     | `http://localhost:11434`               | Where the model is served                            |
| `health_check` | `http://localhost:11434/api/version`   | A URL the platform can call to check the model is up |
| `adapter_type` | `ollama`                               | Which adapter translates platform requests into the provider's API |

After registering the model, the example queries it like any other model:

- `get_llm_status(GetLLMStatusRequest(name=...))` returns the model's status, endpoint and when it was last
  checked
- `get_llm_capabilities(GetLLMCapabilitiesRequest(model=...))` returns its capabilities
- `list_registered_llms(...)` lists the registered models and `list_llms(...)` all the models of the platform

Finally, the example refreshes the client's cached providers with `get_llm_providers()`. Once the platform
lists `ollama`, the new provider is used exactly like the built-in ones: the example sends it the same request
as OpenAI and Anthropic, blocking and streamed.

### Current limitations

Registering a model is not yet wired into the LLMs service: the platform acknowledges the registration but does
not store it, the status, capabilities and model listings are placeholders, and requests are not routed to
registered models. Until then, `ollama` does not appear in the providers, and the example logs a warning
instead of sending it the request. The client code in this example does not need to change once the platform
supports it.

## Driver code

The complete code of the example, `example_3.py`:

```python
"""This example illustrates the LLMModelClient in gogi using several
model providers: OpenAI and Anthropic, which the platform supports out of
the box, and Ollama, which we add as a new provider.

The same request (a system prompt and a user question) is sent to
OpenAI and Anthropic, first as a blocking request and then as a streamed one,
so the responses, finish reasons and token usage can be compared.

The example then shows how to add a new LLM provider by registering a
model served by a local Ollama server:

- Register the model with its endpoint, health check and capabilities
- Query the model's status and capabilities
- Query the registered models and all the models of the platform
- Send the same request to the new provider

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

# the (provider, model) pairs the platform supports out of the box
PROVIDER_MODELS = [
    ("openai", "gpt-4o-mini"),
    ("anthropic", "claude-opus-5-5"),
]

# the new provider: a model served by a local Ollama server.
# Pull the model first with `ollama pull llama3.2`
OLLAMA_PROVIDER = "ollama"
OLLAMA_MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434"

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


def run_provider(platform: Gogi, provider: str, model: str) -> None:
    request = build_request(provider=provider, model=model)

    try:
        rich_print(Rule(f"{provider} / {model}: blocking request"))
        run_blocking(platform, request)

        rich_print(Rule(f"{provider} / {model}: streamed request"))
        run_streamed(platform, request)
    except (ValueError, grpc.RpcError) as e:
        # e.g. the model is not supported or the provider's API key is not set;
        # report it and carry on
        logger.error(f"Request to {provider}/{model} failed: {e}")


def add_ollama_provider(platform: Gogi) -> None:
    # A new provider is added by registering a model it serves. The registration
    # tells the platform where the model is served (endpoint), how to check that
    # it is up (health_check), which adapter talks to it (adapter_type) and what
    # the model can do (capabilities).
    registration = LLMRegisterRequest(
        info=LLMModelInfo(
            name=OLLAMA_MODEL,
            provider=OLLAMA_PROVIDER,
            capabilities=LLMCapabilities(
                context_window=128_000,
                supports_json_mode=True,
                supports_streaming=True,
                supports_tools=True,
                supports_vision=False,
            ),
        ),
        endpoint=OLLAMA_URL,
        health_check=f"{OLLAMA_URL}/api/version",
        adapter_type=OLLAMA_PROVIDER,
    )
    registration_response = platform.llm_clients.register_llm(registration)
    rich_print(f"Model registration response {registration_response}")

    # check the status of the new model
    status_response = platform.llm_clients.get_llm_status(GetLLMStatusRequest(name=OLLAMA_MODEL))
    rich_print(f"LLM status response {status_response}")

    # get the capabilities of the new model
    capabilities_response = platform.llm_clients.get_llm_capabilities(GetLLMCapabilitiesRequest(model=OLLAMA_MODEL))
    rich_print(f"LLM capabilities response {capabilities_response}")

    # the models registered with the platform
    registered_response = platform.llm_clients.list_registered_llms(ListRegisteredLLMsRequest())
    rich_print(f"Registered LLMs response {registered_response}")

    # all the models of the platform, built-in and registered
    list_response = platform.llm_clients.list_llms(ListLLMsRequest())
    rich_print(f"List LLMs response {list_response}")

    # The client caches the providers, so refresh them to pick up the new one.
    # Once the platform routes requests to registered models, the new provider
    # is used exactly like the built-in ones.
    platform.llm_clients.get_llm_providers()
    if OLLAMA_PROVIDER in platform.llm_clients.providers:
        run_provider(platform, OLLAMA_PROVIDER, OLLAMA_MODEL)
    else:
        logger.warning(
            f"The platform does not route requests to the {OLLAMA_PROVIDER} provider yet; "
            f"available providers are {platform.llm_clients.providers}"
        )


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
    for provider, model in PROVIDER_MODELS:
        run_provider(platform, provider, model)

    # add Ollama as a new provider
    rich_print(Rule("Adding a new provider: Ollama"))
    add_ollama_provider(platform)
```
