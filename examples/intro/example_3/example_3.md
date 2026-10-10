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
