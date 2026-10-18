from unittest.mock import MagicMock

from gogi.clients.credentials_client import CredentialsClient
from gogi.gogi import Gogi
from gogi.v1 import credential_service_pb2 as pb2


def _client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(CredentialsClient)
    client.logger = None
    client._route_metadata = (("authorization", "Bearer gogi_key"),)
    client._stub = MagicMock()
    return client


def test_store():
    client = _client()
    client._stub.StoreCredential.return_value = pb2.StoreCredentialResponse(
        credential=pb2.Credential(
            name="anthropic", created_at="2026-10-18T10:00:00Z", updated_at="2026-10-18T11:00:00Z"
        )
    )

    credential = client.store("anthropic", "sk-ant-secret")

    assert credential.name == "anthropic" and credential.updated_at == "2026-10-18T11:00:00Z"
    request = client._stub.StoreCredential.call_args.args[0]
    assert (request.name, request.value) == ("anthropic", "sk-ant-secret")
    assert ("authorization", "Bearer gogi_key") in client._stub.StoreCredential.call_args.kwargs["metadata"]


def test_list_gives_no_values():
    client = _client()
    client._stub.ListCredentials.return_value = pb2.ListCredentialsResponse(
        credentials=[pb2.Credential(name="anthropic"), pb2.Credential(name="model-key")]
    )

    credentials = client.list()

    assert [c.name for c in credentials] == ["anthropic", "model-key"]
    assert "value" not in credentials[0].model_dump()


def test_every_call_carries_the_applications_key(monkeypatch):
    monkeypatch.delenv("GOGI_API_KEY", raising=False)
    assert ("authorization", "Bearer gogi_key") in Gogi(api_key="gogi_key").indexes.route_metadata
    # without a key, as where gogi runs without keys, none is sent
    assert all(name != "authorization" for name, _ in Gogi().indexes.route_metadata)

    monkeypatch.setenv("GOGI_API_KEY", "gogi_from_env")
    assert ("authorization", "Bearer gogi_from_env") in Gogi().documents.route_metadata


def test_root_certificates_from_a_file(tmp_path, monkeypatch):
    ca = tmp_path / "gogi-ca.pem"
    ca.write_bytes(b"-----BEGIN CERTIFICATE-----\n")
    monkeypatch.setenv("GOGI_GATEWAY_CA_FILE", str(ca))

    assert Gogi(gateway_url="gogi.internal:443").root_certificates == b"-----BEGIN CERTIFICATE-----\n"
    assert Gogi(root_certificates=b"given").root_certificates == b"given"
