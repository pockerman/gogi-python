import json
from unittest.mock import MagicMock

import pytest

from gogi.clients.grpc_helpers.llm_tools_client_grpc_helpers import (
    LLMToolsClientGRPCHelper,
)
from gogi.clients.llm_tools_client import (
    LLMToolsClient,
    model_function_name,
    parameters_schema,
)
from gogi.models.llm.llm_tool_definition import LLMToolCall, ToolCallFunction
from gogi.models.llm.llm_tool_service_definition import LLMToolBehavior
from gogi.models.llm.requests.llm_tools.llm_execute_tool_request import (
    LLMExecuteToolRequest,
)
from gogi.models.llm.requests.llm_tools.llm_get_task_request import LLMGetTaskRequest
from gogi.v1 import llm_tool_pb2, llm_tool_service_pb2


@pytest.fixture
def client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(LLMToolsClient)
    client._grpc_helper = LLMToolsClientGRPCHelper()
    client._route_metadata = ()
    client._stub = MagicMock()
    return client


def booking_tool(version: str = "1.0.0") -> llm_tool_pb2.ToolServiceDefinition:
    return llm_tool_pb2.ToolServiceDefinition(
        name="healthcare.scheduling.book_appointment",
        version=version,
        description="Book an appointment slot for a patient",
        parameters_json='{"type": "object", "properties": {"slot_id": {"type": "string"}}}',
        behavior=llm_tool_pb2.ToolBehavior(requires_confirmation=True),
    )


# ---------------------------------------------------------------------------
# parameters_schema and model_function_name
# ---------------------------------------------------------------------------


def test_parameters_schema_from_shorthand():
    schema = parameters_schema(
        {
            "patient_id": {"type": "string", "description": "Patient identifier"},
            "notes": {"type": "string", "optional": True},
        }
    )
    assert schema == {
        "type": "object",
        "properties": {
            "patient_id": {"type": "string", "description": "Patient identifier"},
            "notes": {"type": "string"},
        },
        "required": ["patient_id"],
    }


def test_parameters_schema_keeps_a_complete_schema():
    schema = {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}
    assert parameters_schema(schema) is schema
    assert parameters_schema(None) == {"type": "object", "properties": {}}


def test_model_function_name():
    assert model_function_name("healthcare.scheduling.book_appointment") == "healthcare__scheduling__book_appointment"

    long_name = "org." + "a" * 80 + ".tool"
    other_long_name = "org." + "a" * 80 + ".other"
    assert len(model_function_name(long_name)) == 64
    assert model_function_name(long_name) != model_function_name(other_long_name)


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


def test_register_builds_the_definition(client):
    client._stub.RegisterTool.return_value = llm_tool_service_pb2.RegisterToolResponse(
        name="healthcare.scheduling.book_appointment", version="1.0.0", status="registered"
    )

    response = client.register(
        name="healthcare.scheduling.book_appointment",
        description="Book an appointment slot for a patient",
        parameters={"patient_id": {"type": "string"}, "slot_id": {"type": "string"}},
        endpoint="https://api.clinic-scheduler.com/v1/bookings",
        credential_ref="scheduling-api-prod",
        behavior={"is_read_only": False, "is_idempotent": False},
        rate_limits={"requests_per_session": 3},
        capabilities=["appointments"],
    )

    assert response.status == "registered"
    tool = client._stub.RegisterTool.call_args.args[0].tool
    assert tool.name == "healthcare.scheduling.book_appointment"
    assert tool.version == "1.0.0"
    assert json.loads(tool.parameters_json)["required"] == ["patient_id", "slot_id"]
    assert tool.endpoint == "https://api.clinic-scheduler.com/v1/bookings"
    assert tool.credential_ref == "scheduling-api-prod"
    assert tool.rate_limits.requests_per_session == 3
    assert not tool.behavior.is_idempotent
    assert list(tool.capabilities) == ["appointments"]
    assert not tool.HasField("execution_limits")


# ---------------------------------------------------------------------------
# discover and build_model_tools
# ---------------------------------------------------------------------------


def test_discover(client):
    client._stub.DiscoverTools.return_value = llm_tool_service_pb2.DiscoverToolsResponse(
        tools=[booking_tool()], relevance_scores={"healthcare.scheduling.book_appointment": 1.0}
    )

    tools = client.discover(namespace="healthcare.scheduling.*", version_constraint="^1.0.0")

    grpc_request = client._stub.DiscoverTools.call_args.args[0]
    assert grpc_request.namespace == "healthcare.scheduling.*"
    assert grpc_request.version_constraint == "^1.0.0"
    assert [tool.name for tool in tools] == ["healthcare.scheduling.book_appointment"]
    assert tools[0].behavior == LLMToolBehavior(requires_confirmation=True)


def test_build_model_tools(client):
    client._stub.DiscoverTools.return_value = llm_tool_service_pb2.DiscoverToolsResponse(tools=[booking_tool()])

    definitions, tool_names = client.build_model_tools(namespace="healthcare.scheduling")

    assert len(definitions) == 1
    assert definitions[0].tool_type == "function"
    assert definitions[0].function.name == "healthcare__scheduling__book_appointment"
    assert definitions[0].function.description == "Book an appointment slot for a patient"
    assert json.loads(definitions[0].function.parameters_json)["properties"] == {"slot_id": {"type": "string"}}
    assert tool_names == {"healthcare__scheduling__book_appointment": "healthcare.scheduling.book_appointment"}


# ---------------------------------------------------------------------------
# execute, validate and tasks
# ---------------------------------------------------------------------------


def test_execute(client):
    client._stub.ExecuteTool.return_value = llm_tool_service_pb2.ExecuteToolResponse(
        success=True, result_json='{"booking_id": "b-1"}', execution_time_ms=12, tool_version="1.0.0"
    )

    response = client.execute(
        "healthcare.scheduling.book_appointment",
        {"slot_id": "s-1"},
        session_id="session-1",
        version="1.0.0",
        confirmed=True,
    )

    grpc_request = client._stub.ExecuteTool.call_args.args[0]
    assert grpc_request.tool_name == "healthcare.scheduling.book_appointment"
    assert json.loads(grpc_request.arguments_json) == {"slot_id": "s-1"}
    assert grpc_request.session_id == "session-1"
    assert grpc_request.version == "1.0.0"
    assert grpc_request.confirmed is True
    assert response.success is True
    assert response.tool_version == "1.0.0"
    assert json.loads(response.result_json) == {"booking_id": "b-1"}


def test_execute_tool_passes_version_and_confirmation(client):
    client._stub.ExecuteTool.return_value = llm_tool_service_pb2.ExecuteToolResponse(
        success=False, error="tool healthcare.scheduling.book_appointment requires confirmation"
    )

    response = client.execute_tool(LLMExecuteToolRequest(tool_name="healthcare.scheduling.book_appointment"))

    grpc_request = client._stub.ExecuteTool.call_args.args[0]
    assert grpc_request.version == ""
    assert grpc_request.confirmed is False
    assert response.success is False
    assert "requires confirmation" in response.error


def test_validate(client):
    client._stub.ValidateTool.return_value = llm_tool_service_pb2.ValidateToolResponse(
        valid=False, errors=["/: missing property 'slot_id'"]
    )

    response = client.validate("healthcare.scheduling.book_appointment", {"patient_id": "p-1"}, version="2.0.0")

    grpc_request = client._stub.ValidateTool.call_args.args[0]
    assert grpc_request.version == "2.0.0"
    assert json.loads(grpc_request.arguments_json) == {"patient_id": "p-1"}
    assert response.valid is False
    assert response.errors == ["/: missing property 'slot_id'"]


def test_execute_async_and_get_task(client):
    client._stub.ExecuteToolAsync.return_value = llm_tool_service_pb2.ExecuteToolAsyncResponse(
        task_id="task-1", status="pending"
    )
    client._stub.GetTask.return_value = llm_tool_service_pb2.GetTaskResponse(
        task_id="task-1", status="succeeded", result_json='{"covered": true}'
    )

    task = client.execute_async("healthcare.billing.verify_insurance", {"patient_id": "p-1"})
    assert task.task_id == "task-1"
    assert task.status == "pending"

    # by task id, or by request
    assert client.get_task(task.task_id).status == "succeeded"
    assert client.get_task(LLMGetTaskRequest(task_id="task-1")).result_json == '{"covered": true}'
    assert client._stub.GetTask.call_args.args[0].task_id == "task-1"


def test_execute_tool_call(client):
    client._stub.ExecuteTool.return_value = llm_tool_service_pb2.ExecuteToolResponse(success=True, result_json="{}")
    tool_names = {"healthcare__scheduling__book_appointment": "healthcare.scheduling.book_appointment"}

    tool_call = LLMToolCall(
        idx="call-1",
        tool_type="function",
        function=ToolCallFunction(name="healthcare__scheduling__book_appointment", arguments='{"slot_id": "s-1"}'),
    )
    response = client.execute_tool_call(tool_call, tool_names, session_id="session-1", confirmed=True)

    grpc_request = client._stub.ExecuteTool.call_args.args[0]
    assert grpc_request.tool_name == "healthcare.scheduling.book_appointment"
    assert grpc_request.arguments_json == '{"slot_id": "s-1"}'
    assert grpc_request.confirmed is True
    assert response.success is True

    unknown = LLMToolCall(idx="call-2", tool_type="function", function=ToolCallFunction(name="other", arguments="{}"))
    response = client.execute_tool_call(unknown, tool_names)
    assert response.success is False
    assert response.error == "unknown tool other"
