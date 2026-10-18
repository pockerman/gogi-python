from gogi.clients.base_client import BaseClient
from gogi.models.credential import Credential
from gogi.v1 import credential_service_pb2 as pb2
from gogi.v1 import credential_service_pb2_grpc as pb2_grpc

# the credentials of the built-in providers: an application's calls to them are made with its own key
ANTHROPIC = "anthropic"
OPENAI = "openai"


def _credential(credential: pb2.Credential) -> Credential:
    return Credential(name=credential.name, created_at=credential.created_at, updated_at=credential.updated_at)


class CredentialsClient(BaseClient):
    """The application's own credentials: its model providers' keys, and the keys its registered models need.

    A credential's value is kept in gogi's credential store and never given back; another application cannot
    use it.
    """

    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llms", logger=logger)
        self._stub = pb2_grpc.CredentialServerStub(self._channel)

    def store(self, name: str, value: str) -> Credential:
        """Stores the credential, e.g. ``store("anthropic", key)``; storing one the application has replaces its
        value."""
        response = self._stub.StoreCredential(
            pb2.StoreCredentialRequest(name=name, value=value), metadata=self.route_metadata
        )
        return _credential(response.credential)

    def list(self) -> list[Credential]:
        """The application's credentials, without their values."""
        response = self._stub.ListCredentials(pb2.ListCredentialsRequest(), metadata=self.route_metadata)
        return [_credential(credential) for credential in response.credentials]
