from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Service availability response."""

    status: str = Field(description="Current service availability.")
    service: str = Field(description="Name of the running service.")
    environment: str = Field(description="Active deployment environment.")
