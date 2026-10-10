import uuid
from unittest.mock import MagicMock

import pytest

from gogi.clients.grpc_helpers.llm_models_client_grpc_helpers import (
    LLMModelsClientGRPCHelper,
)
from gogi.clients.llm_models_client import LLMModelsClient
from gogi.models import (
    LLMCapabilities,
    LLMModelInfo,
    LLMRegisterRequest,
    LLMRunRequest,
    LLMRunRequestConfig,
    LLMTokenUsage,
    LLMToolCall,
    ToolCallFunction,
)
from gogi.v1 import llm_model_service_pb2


@pytest.fixture
def llm_request():
    return LLMRunRequest(
        messages=[],
        config=LLMRunRequestConfig(provider="anthropic", model="claude-3-5-sonnet", temperature=0.0, top_p=1.0),
    )


@pytest.fixture
def client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(LLMModelsClient)

    client._grpc_helper = LLMModelsClientGRPCHelper()
    client._route_metadata = ()

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


def _grpc_tool_call(idx: str, tool_type: str, name: str, arguments: str) -> MagicMock:
    # "name" is reserved by Mock's constructor (sets the mock's repr name),
    # so the function's own name must be assigned as an attribute afterwards.
    function = MagicMock(arguments=arguments)
    function.name = name
    return MagicMock(id=idx, type=tool_type, function=function)


# ---------------------------------------------------------------------------
# validate_provider_in_request
# ---------------------------------------------------------------------------


def test_validate_provider_success(llm_request):
    LLMModelsClientGRPCHelper.validate_provider_in_request(
        request=llm_request,
        providers=["anthropic", "openai"],
    )


def test_validate_provider_failure(llm_request):
    llm_request.config.provider = "gemini"

    with pytest.raises(ValueError):
        LLMModelsClientGRPCHelper.validate_provider_in_request(
            request=llm_request,
            providers=["anthropic", "openai"],
        )


# ---------------------------------------------------------------------------
# validate_provider_supports_model
# ---------------------------------------------------------------------------


def test_validate_provider_supports_model_success(llm_request):
    LLMModelsClientGRPCHelper.validate_provider_supports_model(
        request=llm_request,
        models=["claude-3-5-sonnet", "claude-3-7-sonnet"],
    )


def test_validate_provider_supports_model_none(llm_request):
    with pytest.raises(ValueError):
        LLMModelsClientGRPCHelper.validate_provider_supports_model(
            request=llm_request,
            models=None,
        )


def test_validate_provider_supports_model_unknown_model(llm_request):
    llm_request.config.model = "claude-4"

    with pytest.raises(ValueError):
        LLMModelsClientGRPCHelper.validate_provider_supports_model(
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
        client._grpc_helper,
        "validate_provider_in_request",
        validate_provider,
    )

    monkeypatch.setattr(
        client._grpc_helper,
        "validate_provider_supports_model",
        validate_model,
    )

    grpc_request = MagicMock()
    monkeypatch.setattr(
        client._grpc_helper,
        "build_grpc_request",
        lambda req: grpc_request,
    )

    grpc_response = MagicMock(
        content="hello",
        model="claude-3-5-sonnet",
        provider="anthropic",
        finish_reason="stop",
        usage=LLMTokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        tool_calls=[],
    )

    client._stub = MagicMock()
    client._stub.Run.return_value = grpc_response

    client.run(llm_request)

    assert called["provider"]
    assert called["model"]


def test_run_calls_stub(client, llm_request, monkeypatch):
    grpc_request = MagicMock()

    monkeypatch.setattr(
        client._grpc_helper,
        "build_grpc_request",
        lambda req: grpc_request,
    )

    grpc_response = MagicMock(
        content="hello",
        model="claude",
        provider="anthropic",
        finish_reason="stop",
        usage=LLMTokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        tool_calls=[],
    )

    client._stub = MagicMock()
    client._stub.Run.return_value = grpc_response
    client.run(llm_request)
    client._stub.Run.assert_called_once_with(grpc_request, metadata=client.route_metadata)


def test_run_returns_llm_response(client, llm_request, monkeypatch):
    monkeypatch.setattr(
        client._grpc_helper,
        "build_grpc_request",
        lambda req: MagicMock(),
    )

    usage = LLMTokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)

    idx = uuid.uuid4().hex
    grpc_tool_calls = [_grpc_tool_call(idx=idx, tool_type="test_function", name="Testfunction", arguments="a:1, b:2")]
    expected_tool_calls = [
        LLMToolCall(
            idx=idx, tool_type="test_function", function=ToolCallFunction(name="Testfunction", arguments="a:1, b:2")
        )
    ]

    grpc_response = MagicMock(
        content="Hello world",
        model="claude-3-5-sonnet",
        provider="anthropic",
        finish_reason="stop",
        usage=usage,
        tool_calls=grpc_tool_calls,
    )

    client._stub = MagicMock()
    client._stub.Run.return_value = grpc_response

    response = client.run(llm_request)

    assert response.content == "Hello world"
    assert response.model == "claude-3-5-sonnet"
    assert response.provider == "anthropic"
    assert response.finish_reason == "stop"
    assert response.token_usage == usage
    assert response.tool_calls == expected_tool_calls


def test_run_builds_grpc_request(client, llm_request, monkeypatch):
    called = False

    grpc_request = MagicMock()

    def build(req):
        nonlocal called
        called = True
        assert req is llm_request
        return grpc_request

    monkeypatch.setattr(
        client._grpc_helper,
        "build_grpc_request",
        build,
    )

    grpc_response = MagicMock(
        content="",
        model="",
        provider="",
        finish_reason="",
        usage=LLMTokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        tool_calls=[],
    )

    client._stub = MagicMock()
    client._stub.Run.return_value = grpc_response

    client.run(llm_request)

    assert called


def _registration_request(credential_ref: str = "") -> LLMRegisterRequest:
    return LLMRegisterRequest(
        info=LLMModelInfo(
            name="healthfirst-medical-v1",
            provider="custom",
            capabilities=LLMCapabilities(
                context_window=8192,
                supports_vision=False,
                supports_tools=True,
                supports_streaming=True,
                supports_json_mode=False,
            ),
        ),
        endpoint="http://ml-inference.internal:8000/v1",
        health_check="/health",
        adapter_type="openai",
        credential_ref=credential_ref,
    )


def test_build_grpc_registration_request_with_credential_ref():
    grpc_request = LLMModelsClientGRPCHelper.build_grpc_registration_request(
        _registration_request(credential_ref="ml-inference-prod")
    )

    assert grpc_request.info.name == "healthfirst-medical-v1"
    assert grpc_request.endpoint == "http://ml-inference.internal:8000/v1"
    assert grpc_request.health_check == "/health"
    assert grpc_request.credential_ref == "ml-inference-prod"


def test_build_grpc_registration_request_without_credential_ref():
    grpc_request = LLMModelsClientGRPCHelper.build_grpc_registration_request(_registration_request())

    assert grpc_request.credential_ref == ""


def test_serialize_registered_llms_with_credential_ref():
    grpc_response = llm_model_service_pb2.ListRegisteredLLMsResponse(
        models=[
            llm_model_service_pb2.RegisteredLLM(
                info=llm_model_service_pb2.ModelInfo(name="healthfirst-medical-v1", provider="custom"),
                endpoint="http://ml-inference.internal:8000/v1",
                health_check="/health",
                status="provisioning",
                registered_at="2026-10-10T12:00:00Z",
                adapter_type="openai",
                credential_ref="ml-inference-prod",
            )
        ]
    )

    response = LLMModelsClientGRPCHelper.serialize_list_registered_llms_grpc_response(grpc_response)

    assert response.models[0].credential_ref == "ml-inference-prod"
    assert response.models[0].status == "provisioning"
