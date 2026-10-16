from unittest.mock import MagicMock

import grpc
import pytest
from grpc_health.v1 import health_pb2

from gogi.clients.health_client import PLATFORM_SERVICES, HealthClient
from gogi.models.health import ServingStatus

SERVING = health_pb2.HealthCheckResponse.SERVING
NOT_SERVING = health_pb2.HealthCheckResponse.NOT_SERVING


class FakeRpcError(grpc.RpcError):
    def __init__(self, code: grpc.StatusCode, details: str = ""):
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


@pytest.fixture
def client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(HealthClient)
    client.logger = None
    client.platform = MagicMock(gateway_url="localhost:50051")
    client._route_metadata = ()
    client._timeout_seconds = 1.0
    client._stub = MagicMock()
    return client


def _answer(statuses: dict[str, int | Exception]):
    """A stub Check that answers with the status, or raises the error, given for the requested service."""

    def check(request, metadata=None, timeout=None):
        answer = statuses[request.service]
        if isinstance(answer, Exception):
            raise answer
        return health_pb2.HealthCheckResponse(status=answer)

    return check


def test_check_gateway_asks_for_the_empty_service(client):
    client._stub.Check.side_effect = _answer({"": SERVING})

    assert client.check() == ServingStatus.SERVING
    assert client._stub.Check.call_args.args[0].service == ""


def test_check_service(client):
    client._stub.Check.side_effect = _answer({"llms": NOT_SERVING})

    assert client.check("llms") == ServingStatus.NOT_SERVING


def test_check_raises_for_unknown_service(client):
    client._stub.Check.side_effect = _answer({"nope": FakeRpcError(grpc.StatusCode.NOT_FOUND)})

    with pytest.raises(grpc.RpcError):
        client.check("nope")


def test_status_when_everything_is_serving(client):
    client._stub.Check.side_effect = _answer({"": SERVING, **dict.fromkeys(PLATFORM_SERVICES, SERVING)})

    health = client.status()

    assert health.reachable
    assert health.serving
    assert set(health.services) == {"gateway", *PLATFORM_SERVICES}


def test_status_reports_the_services_that_are_not_serving(client):
    statuses = {"": SERVING, **dict.fromkeys(PLATFORM_SERVICES, SERVING)}
    statuses["llms"] = NOT_SERVING
    statuses["guardrails"] = FakeRpcError(grpc.StatusCode.NOT_FOUND)
    statuses["prompts"] = FakeRpcError(grpc.StatusCode.DEADLINE_EXCEEDED)
    client._stub.Check.side_effect = _answer(statuses)

    health = client.status()

    assert health.reachable
    assert not health.serving
    assert health.not_serving == ["guardrails", "llms", "prompts"]
    assert health.services["guardrails"] == ServingStatus.SERVICE_UNKNOWN
    assert health.services["prompts"] == ServingStatus.UNKNOWN


def test_status_does_not_raise_when_the_gateway_is_unreachable(client):
    client._stub.Check.side_effect = FakeRpcError(grpc.StatusCode.UNAVAILABLE, "connection refused")

    health = client.status()

    assert not health.reachable
    assert not health.serving
    assert health.services == {}
    assert health.error == "UNAVAILABLE: connection refused"
