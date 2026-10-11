import json
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from gogi.clients.grpc_helpers.llm_sessions_client_grpc_helpers import (
    LLMSessionsClientGRPCHelper,
)
from gogi.clients.llm_sessions_client import LLMSessionMemoryManager, LLMSessionsClient
from gogi.models import (
    AddMessagesToLLMSessionRequest,
    CreateLLMSessionRequest,
    DeleteLLMSessionMemoryRequest,
    DeleteLLMSessionRequest,
    GetLLMSessionMemoryRequest,
    GetMessagesFromLLMSessionRequest,
    ListLLMSessionsRequest,
    LLMMessage,
    LLMToolCall,
    SaveLLMSessionMemoryRequest,
    ToolCallFunction,
)
from gogi.v1 import llm_message_pb2, llm_tool_pb2
from gogi.v1 import llm_session_service_pb2 as pb2

# The fixtures are a user planning a cycling holiday with an assistant


def _bare(cls):
    # avoid calling __init__, which creates a gRPC channel
    client = object.__new__(cls)
    client._grpc_helper = LLMSessionsClientGRPCHelper()
    client._route_metadata = (("x-target-service", "llm-sessions"),)
    client._stub = MagicMock()
    return client


@pytest.fixture
def client():
    client = _bare(LLMSessionsClient)
    client._memory_manager = _bare(LLMSessionMemoryManager)
    return client


def _session(**overrides) -> pb2.Session:
    fields = {
        "session_id": "alps-2027",
        "user_id": "u-31",
        "created_at": 1760000000000,
        "updated_at": 1760000005000,
        "message_count": 4,
    }
    fields.update(overrides)
    return pb2.Session(**fields)


def test_get_or_create_session(client):
    client._stub.GetOrCreateSession.return_value = pb2.GetOrCreateSessionResponse(session=_session(), created=True)

    session = client.get_or_create_session(CreateLLMSessionRequest(user_id="u-31", session_id="alps-2027"))

    grpc_request = client._stub.GetOrCreateSession.call_args.args[0]
    assert (grpc_request.user_id, grpc_request.session_id) == ("u-31", "alps-2027")
    assert client._stub.GetOrCreateSession.call_args.kwargs["metadata"] == client._route_metadata
    assert session.created is True
    assert session.message_count == 4
    # timestamps are unix millis
    assert session.created_at.timestamp() == 1760000000
    assert session.updated_at.timestamp() == 1760000005


def test_get_or_create_session_without_id(client):
    client._stub.GetOrCreateSession.return_value = pb2.GetOrCreateSessionResponse(session=_session())

    client.get_or_create_session(CreateLLMSessionRequest(user_id="u-31"))

    assert not client._stub.GetOrCreateSession.call_args.args[0].HasField("session_id")


def test_list_and_delete_sessions(client):
    client._stub.ListSessions.return_value = pb2.ListSessionsResponse(
        sessions=[_session(), _session(session_id="dolomites")], total_count=7
    )
    client._stub.DeleteSession.return_value = pb2.DeleteSessionResponse(success=True)

    listed = client.list_sessions(ListLLMSessionsRequest(user_id="u-31", limit=2, offset=4))
    deleted = client.delete_session(DeleteLLMSessionRequest(session_id="alps-2027", delete_memories=True))

    grpc_request = client._stub.ListSessions.call_args.args[0]
    assert (grpc_request.limit, grpc_request.offset) == (2, 4)
    assert [s.session_id for s in listed.sessions] == ["alps-2027", "dolomites"]
    assert listed.total_count == 7
    assert client._stub.DeleteSession.call_args.args[0].delete_memories is True
    assert deleted.success is True


def test_add_messages_keeps_optional_fields_unset(client):
    client._stub.AddMessages.return_value = pb2.AddMessagesResponse(success=True, message_count=2, total_count=6)
    call = LLMToolCall(
        idx="c1", tool_type="function", function=ToolCallFunction(name="route", arguments='{"from":"Innsbruck"}')
    )

    response = client.add_messages_to_session(
        AddMessagesToLLMSessionRequest(
            session_id="alps-2027",
            messages=[
                LLMMessage(role="assistant", tool_calls=[call]),
                LLMMessage.tool_result(call, '{"km": 84}'),
            ],
        )
    )

    calling, result = client._stub.AddMessages.call_args.args[0].messages
    # an assistant message that only calls tools has no content, not an empty one
    assert not calling.HasField("content")
    assert not calling.HasField("tool_call_id")
    assert calling.tool_calls[0].function.name == "route"
    assert result.tool_call_id == "c1"
    assert response.total_count == 6


def test_get_messages_with_a_strategy(client):
    client._stub.GetMessages.return_value = pb2.GetMessagesResponse(
        messages=[
            llm_message_pb2.LLMMessage(role="system", content="Summary of the 12 earlier messages: ..."),
            llm_message_pb2.LLMMessage(
                role="assistant",
                tool_calls=[
                    llm_tool_pb2.ToolCall(
                        id="c2", type="function", function=llm_tool_pb2.ToolCallFunction(name="weather", arguments="{}")
                    )
                ],
            ),
        ],
        total_count=20,
        strategy="summarize",
        omitted_count=12,
        summarized_count=12,
        summary="The user plans a week in the Alps.",
        estimated_tokens=480,
        notes=["a note"],
    )

    response = client.get_messages(
        GetMessagesFromLLMSessionRequest(
            session_id="alps-2027", strategy="summarize", token_budget=2000, summary_focus="dates and distances"
        )
    )

    grpc_request = client._stub.GetMessages.call_args.args[0]
    assert (grpc_request.strategy, grpc_request.token_budget, grpc_request.summary_focus) == (
        "summarize",
        2000,
        "dates and distances",
    )
    assert not grpc_request.HasField("limit")
    assert response.strategy == "summarize"
    assert (response.omitted_count, response.summarized_count, response.estimated_tokens) == (12, 12, 480)
    assert response.summary == "The user plans a week in the Alps."
    assert response.notes == ["a note"]
    assert response.messages[1].content is None
    assert response.messages[1].tool_calls[0].function.name == "weather"


def test_get_messages_request_validation():
    with pytest.raises(ValidationError):
        GetMessagesFromLLMSessionRequest(session_id="s", strategy="everything")
    with pytest.raises(ValidationError):
        GetMessagesFromLLMSessionRequest(session_id="s", token_budget=0)


def test_save_memory_encodes_values_as_json(client):
    client._memory_manager._stub.SaveMemory.return_value = pb2.SaveMemoryResponse(
        success=True,
        entry=pb2.MemoryEntry(key="bike", value='{"type": "gravel", "gears": 22}', created_at=1, updated_at=2),
    )

    response = client.save_memory(
        SaveLLMSessionMemoryRequest(user_id="u-31", key="bike", value={"type": "gravel", "gears": 22})
    )

    grpc_request = client._memory_manager._stub.SaveMemory.call_args.args[0]
    assert json.loads(grpc_request.value) == {"type": "gravel", "gears": 22}
    assert not grpc_request.HasField("session_id")
    assert not grpc_request.HasField("expected_updated_at")
    assert response.entry.value == {"type": "gravel", "gears": 22}
    assert response.entry.session_id is None
    assert response.entry.updated_at == 2


def test_save_memory_with_expected_updated_at(client):
    client._memory_manager._stub.SaveMemory.return_value = pb2.SaveMemoryResponse(success=True)

    client.save_memory(
        SaveLLMSessionMemoryRequest(
            user_id="u-31", key="pace", value="relaxed", session_id="alps-2027", expected_updated_at=0
        )
    )

    grpc_request = client._memory_manager._stub.SaveMemory.call_args.args[0]
    # a string is sent as a JSON string
    assert grpc_request.value == '"relaxed"'
    assert grpc_request.HasField("expected_updated_at")
    assert grpc_request.expected_updated_at == 0
    assert grpc_request.session_id == "alps-2027"


def test_get_and_delete_memory(client):
    client._memory_manager._stub.GetMemory.return_value = pb2.GetMemoryResponse(
        memories={"bike": '"gravel"', "daily_km": "70"},
        entries=[
            pb2.MemoryEntry(key="bike", value='"gravel"'),
            pb2.MemoryEntry(key="daily_km", value="70", session_id="alps-2027"),
        ],
    )
    client._memory_manager._stub.DeleteMemory.return_value = pb2.DeleteMemoryResponse(success=True, count=2)

    memory = client.get_memory(GetLLMSessionMemoryRequest(user_id="u-31"))
    deleted = client.delete_memory(DeleteLLMSessionMemoryRequest(user_id="u-31", key="bike"))

    assert memory.memories == {"bike": "gravel", "daily_km": 70}
    assert memory.entries[1].session_id == "alps-2027"
    assert (deleted.success, deleted.count) == (True, 2)
