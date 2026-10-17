from unittest.mock import MagicMock

import pytest

from gogi.clients.indexes_client import IndexesClient
from gogi.models.gogi_index import IndexRole
from gogi.v1.data import index_service_pb2


@pytest.fixture
def client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(IndexesClient)
    client.logger = None
    client._route_metadata = ()
    client._stub = MagicMock()
    return client


def _index(members: dict[str, int]) -> index_service_pb2.IndexResponse:
    return index_service_pb2.IndexResponse(
        id="idx-1",
        index_name="maria--aeronautics",
        owner="maria",
        created_at="2026-10-16T10:00:00Z",
        last_updated_at="2026-10-16T10:00:00Z",
        members=[index_service_pb2.IndexMember(user=user, role=role) for user, role in members.items()],
    )


OWNER = index_service_pb2.INDEX_MEMBER_ROLE_OWNER
READER = index_service_pb2.INDEX_MEMBER_ROLE_READER


def test_index_has_its_members(client):
    client._stub.GetIndexByName.return_value = _index({"maria": OWNER, "tom": READER})

    index = client.get_index_by_name("maria--aeronautics")

    assert index.owner == "maria"
    assert index.members == {"maria": IndexRole.OWNER, "tom": IndexRole.READER}


def test_list_member_indexes_asks_by_member(client):
    client._stub.ListIndexes.return_value = index_service_pb2.ListIndexesResponse(indexes=[_index({"maria": OWNER})])

    indexes = client.list_member_indexes("tom")

    request = client._stub.ListIndexes.call_args.args[0]
    assert request.member == "tom"
    assert request.owner_name == ""
    assert [index.index_name for index in indexes] == ["maria--aeronautics"]


@pytest.mark.parametrize("role, proto_role", [(IndexRole.OWNER, OWNER), (IndexRole.READER, READER)])
def test_set_member(client, role, proto_role):
    client._stub.SetIndexMember.return_value = _index({"maria": OWNER, "tom": proto_role})

    index = client.set_member("maria--aeronautics", "tom", role)

    request = client._stub.SetIndexMember.call_args.args[0]
    assert (request.index_name, request.user, request.role) == ("maria--aeronautics", "tom", proto_role)
    assert index.members["tom"] == role


def test_remove_member(client):
    client._stub.RemoveIndexMember.return_value = _index({"maria": OWNER})

    index = client.remove_member("maria--aeronautics", "tom")

    request = client._stub.RemoveIndexMember.call_args.args[0]
    assert (request.index_name, request.user) == ("maria--aeronautics", "tom")
    assert index.members == {"maria": IndexRole.OWNER}
