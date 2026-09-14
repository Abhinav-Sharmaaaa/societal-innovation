from pydantic import BaseModel, Field


class GPSLocationRequest(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
    )

    accuracy_meters: float | None = Field(
        default=None,
        ge=0,
    )


class ManualLocationRequest(BaseModel):
    state: str | None = None
    district: str | None = None
    locality: str | None = None


class LocationResolutionResponse(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    accuracy_meters: float | None = None

    state: str | None = None
    district: str | None = None
    locality: str | None = None

    display_name: str | None = None

    source: str
    verified: bool
    reason: str