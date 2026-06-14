import pytest

from gogi.clients.llm_models_client import LLMModelsClient
from gogi.clients import LLMRequest, LLMRunRequestConfig 


@pytest.fixture
def llm_request():
    return LLMRequest(
        messages=[],
        config=LLMRunRequestConfig(
            provider="anthropic",
            model="claude-3-5-sonnet",
            temperature=0.0,
            top_p=1.0
        ),
    )


@pytest.fixture
def client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(LLMModelsClient)

    client._providers_to_model_cache = {
        "anthropic": [
            "claude-3-5-sonnet",
            "claude-3-7-sonnet",
        ],
        "openai": [
            "gpt-4.1",
            "gpt-4o",
        ],
    }

    return client


# ---------------------------------------------------------------------------
# validate_provider_in_request
# ---------------------------------------------------------------------------

def test_validate_provider_success(llm_request):
    LLMModelsClient.validate_provider_in_request(
        request=llm_request,
        providers=["anthropic", "openai"],
    )


def test_validate_provider_failure(llm_request):
    llm_request.config.provider = "gemini"

    with pytest.raises(ValueError):
        LLMModelsClient.validate_provider_in_request(
            request=llm_request,
            providers=["anthropic", "openai"],
        )


# ---------------------------------------------------------------------------
# validate_provider_supports_model
# ---------------------------------------------------------------------------

def test_validate_provider_supports_model_success(llm_request):
    LLMModelsClient.validate_provider_supports_model(
        request=llm_request,
        models=["claude-3-5-sonnet", "claude-3-7-sonnet"],
    )


def test_validate_provider_supports_model_none(llm_request):
    with pytest.raises(ValueError):
        LLMModelsClient.validate_provider_supports_model(
            request=llm_request,
            models=None,
        )


def test_validate_provider_supports_model_unknown_model(llm_request):
    llm_request.config.model = "claude-4"

    with pytest.raises(ValueError):
        LLMModelsClient.validate_provider_supports_model(
            request=llm_request,
            models=["claude-3-5-sonnet"],
        )


# ---------------------------------------------------------------------------
# providers property
# ---------------------------------------------------------------------------

def test_providers(client):
    providers = client.providers

    assert len(providers) == 2
    assert set(providers) == {"anthropic", "openai"}


# ---------------------------------------------------------------------------
# provider_models
# ---------------------------------------------------------------------------

def test_provider_models(client):
    models = client.provider_models("anthropic")

    assert models == [
        "claude-3-5-sonnet",
        "claude-3-7-sonnet",
    ]


def test_provider_models_unknown_provider(client):
    assert client.provider_models("gemini") is None


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------

def test_run_calls_validation(client, llm_request, monkeypatch):
    called = {
        "provider": False,
        "model": False,
    }

    def validate_provider(*args, **kwargs):
        called["provider"] = True

    def validate_model(*args, **kwargs):
        called["model"] = True

    monkeypatch.setattr(
        LLMModelsClient,
        "validate_provider_in_request",
        staticmethod(validate_provider),
    )

    monkeypatch.setattr(
        LLMModelsClient,
        "validate_provider_supports_model",
        staticmethod(validate_model),
    )

    # run() is currently unfinished, so ignore any exception it raises.
    try:
        client.run(llm_request)
    except Exception:
        pass

    assert called["provider"]
    assert called["model"]