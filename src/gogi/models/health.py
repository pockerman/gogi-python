from enum import StrEnum

from pydantic import BaseModel, Field


class ServingStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    SERVING = "SERVING"
    NOT_SERVING = "NOT_SERVING"
    SERVICE_UNKNOWN = "SERVICE_UNKNOWN"


class PlatformHealth(BaseModel):
    """The health of the platform as the gateway reports it."""

    reachable: bool = Field(..., description="Whether the gateway answered")
    services: dict[str, ServingStatus] = Field(
        default_factory=dict, description="The status of the gateway and of every service behind it, by name"
    )
    error: str | None = Field(None, description="Why the gateway could not be asked, if it was not reachable")

    @property
    def serving(self) -> bool:
        """True if the gateway and every service are serving."""
        return self.reachable and all(status == ServingStatus.SERVING for status in self.services.values())

    @property
    def not_serving(self) -> list[str]:
        """The names of the services that are not serving."""
        return sorted(name for name, status in self.services.items() if status != ServingStatus.SERVING)
