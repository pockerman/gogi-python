from pydantic import BaseModel, Field


class Credential(BaseModel):
    """A credential of the application; never its value."""

    name: str = Field(..., description="e.g. 'anthropic', the key of a built-in provider")
    created_at: str = Field("", description="RFC 3339")
    updated_at: str = Field("", description="RFC 3339")
