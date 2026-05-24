import grpc
import os

from gogi.utils.retry_interceptor import RetryInterceptor


def _use_insecure_channel(gateway_url: str) -> bool:
    """Return True if we should connect with a plaintext gRPC channel.

    Plaintext is used when:
    - the URL points at the local loopback (``localhost``, ``127.0.0.1``), or
    - the env var ``GOGI_GATEWAY_INSECURE=1`` is set — this is how
      compose-network services and locally-launched workflow containers
      opt out of TLS, since the in-cluster gateway is plain gRPC.

    Production deployments leave ``GOGI_GATEWAY_INSECURE`` unset and use
    a public hostname, so the secure-channel path is the default.
    """
    if gateway_url.startswith(("localhost", "127.0.0.1")):
        return True
    return os.environ.get("GOGI_GATEWAY_INSECURE", "0") == "1"


class BaseClient:

    def __init__(self, platform, service_name: str, logger=None):
        self.platform = platform
        self.service_name = service_name
        self.logger = logger

        if _use_insecure_channel(platform.gateway_url):
            raw_channel = grpc.insecure_channel(platform.gateway_url)
        else:
            credentials = grpc.ssl_channel_credentials()
            raw_channel = grpc.secure_channel(platform.gateway_url, credentials)

        self._channel = grpc.intercept_channel(raw_channel, RetryInterceptor())
        self._route_metadata: tuple[tuple[str, str], ...] = (("x-target-service", service_name),)

    @property
    def route_metadata(self) -> tuple[tuple[str, str], ...]:
        return self._route_metadata
