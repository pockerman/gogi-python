import pytest
from unittest.mock import MagicMock

from gogi.clients.guardrails_client import GuardrailsClient
from gogi.clients.grpc_helpers.guardrails_client_grpc_helpers import GuardrailsClientGRPCHelper
from gogi.models.guardrails.requests.check_policy_request import CheckPolicyRequest
from gogi.models.guardrails.requests.filter_output_request import FilterOutputRequest
from gogi.models.guardrails.requests.report_violation_request import ReportViolationRequest
from gogi.models.guardrails.requests.validate_input_request import ValidateInputRequest


@pytest.fixture
def client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(GuardrailsClient)
    client._grpc_helper = GuardrailsClientGRPCHelper()
    client._route_metadata = ()
    client._stub = MagicMock()
    return client


# ---------------------------------------------------------------------------
# validate_input
# ---------------------------------------------------------------------------

def test_validate_input_calls_stub(client):
    grpc_response = MagicMock(allowed=True, denial_reason="", triggered_checks=["pii"])
    client._stub.ValidateInput.return_value = grpc_response

    request = ValidateInputRequest(content="hello", checks=["pii"])
    response = client.validate_input(request)

    client._stub.ValidateInput.assert_called_once()
    grpc_request = client._stub.ValidateInput.call_args.args[0]
    assert grpc_request.content == "hello"
    assert list(grpc_request.checks) == ["pii"]

    assert response.allowed is True
    assert response.triggered_checks == ["pii"]


def test_validate_input_denied(client):
    grpc_response = MagicMock(allowed=False, denial_reason="contains PII", triggered_checks=["pii"])
    client._stub.ValidateInput.return_value = grpc_response

    response = client.validate_input(ValidateInputRequest(content="my ssn is ..."))

    assert response.allowed is False
    assert response.denial_reason == "contains PII"


# ---------------------------------------------------------------------------
# filter_output
# ---------------------------------------------------------------------------

def test_filter_output_calls_stub(client):
    grpc_response = MagicMock(content="redacted", modified=True, applied_filters=["profanity"])
    client._stub.FilterOutput.return_value = grpc_response

    request = FilterOutputRequest(content="original", filters=["profanity"])
    response = client.filter_output(request)

    client._stub.FilterOutput.assert_called_once()
    grpc_request = client._stub.FilterOutput.call_args.args[0]
    assert grpc_request.content == "original"
    assert list(grpc_request.filters) == ["profanity"]

    assert response.content == "redacted"
    assert response.modified is True
    assert response.applied_filters == ["profanity"]


# ---------------------------------------------------------------------------
# check_policy
# ---------------------------------------------------------------------------

def test_check_policy_calls_stub(client):
    grpc_response = MagicMock(
        allowed=False,
        denial_reason="rate limit exceeded",
        violated_rules=["rate_limit"],
        suggested_action="retry_later",
    )
    client._stub.CheckPolicy.return_value = grpc_response

    request = CheckPolicyRequest(policy_name="rate-limits", action="execute_tool", arguments_json="{}")
    response = client.check_policy(request)

    client._stub.CheckPolicy.assert_called_once()
    grpc_request = client._stub.CheckPolicy.call_args.args[0]
    assert grpc_request.policy_name == "rate-limits"
    assert grpc_request.action == "execute_tool"

    assert response.allowed is False
    assert response.violated_rules == ["rate_limit"]
    assert response.suggested_action == "retry_later"


# ---------------------------------------------------------------------------
# report_violation
# ---------------------------------------------------------------------------

def test_report_violation_calls_stub(client):
    grpc_response = MagicMock(violation_id="v-123", recorded=True)
    client._stub.ReportViolation.return_value = grpc_response

    request = ReportViolationRequest(
        policy_name="rate-limits",
        action="execute_tool",
        severity="high",
        details="exceeded 10 requests/min",
    )
    response = client.report_violation(request)

    client._stub.ReportViolation.assert_called_once()
    grpc_request = client._stub.ReportViolation.call_args.args[0]
    assert grpc_request.policy_name == "rate-limits"
    assert grpc_request.severity == "high"

    assert response.violation_id == "v-123"
    assert response.recorded is True
