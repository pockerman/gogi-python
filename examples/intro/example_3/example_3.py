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
