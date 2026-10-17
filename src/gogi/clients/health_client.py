from concurrent.futures import ThreadPoolExecutor

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc

from gogi.clients.base_client import BaseClient
from gogi.models.health import PlatformHealth, ServingStatus

GATEWAY = "gateway"

# the services behind the gateway, by the names the gateway routes them under. The gateway's List would give them
# too, but grpcio-health-checking only has List from versions that need protobuf 6
PLATFORM_SERVICES = (
    "documents",
    "indexes",
    "llms",
    "prompts",
    "llm-sessions",
    "workflows",
    "llm-tools",
    "guardrails",
    "observability",
)


class HealthClient(BaseClient):
    """The platform's health, from the gateway's gRPC health service (grpc.health.v1)."""

    def __init__(self, platform, logger=None, timeout_seconds: float = 5.0):
        super().__init__(platform=platform, service_name=GATEWAY, logger=logger)
        self._stub = health_pb2_grpc.HealthStub(self._channel)
        self._timeout_seconds = timeout_seconds

    def check(self, service: str = GATEWAY) -> ServingStatus:
        """The status of one service, e.g. ``"llms"``, or of the gateway itself.

        Raises ``grpc.RpcError`` with ``NOT_FOUND`` for a service the platform doesn't have, and with
        ``UNAVAILABLE`` if the gateway can't be reached.
        """
        response = self._stub.Check(
            health_pb2.HealthCheckRequest(service="" if service == GATEWAY else service),
            metadata=self.route_metadata,
            timeout=self._timeout_seconds,
        )
        return ServingStatus(health_pb2.HealthCheckResponse.ServingStatus.Name(response.status))

    def status(self) -> PlatformHealth:
        """The status of the gateway and of every service. Doesn't raise if the gateway can't be reached."""
        try:
            gateway = self.check(GATEWAY)
        except grpc.RpcError as e:
            if self.logger:
                self.logger.warning(f"the gateway at {self.platform.gateway_url} did not answer: {e.code().name}")
            return PlatformHealth(reachable=False, error=f"{e.code().name}: {e.details()}")

        with ThreadPoolExecutor(max_workers=len(PLATFORM_SERVICES)) as pool:
            statuses = dict(zip(PLATFORM_SERVICES, pool.map(self._check_quietly, PLATFORM_SERVICES)))
        return PlatformHealth(reachable=True, services={GATEWAY: gateway, **statuses})

    def _check_quietly(self, service: str) -> ServingStatus:
        try:
            return self.check(service)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return ServingStatus.SERVICE_UNKNOWN
            return ServingStatus.UNKNOWN
