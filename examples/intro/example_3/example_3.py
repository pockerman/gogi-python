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
