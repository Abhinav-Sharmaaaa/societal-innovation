import httpx

from fastapi import APIRouter, HTTPException

from app.schemas.location import (
    GPSLocationRequest,
    ManualLocationRequest,
    LocationResolutionResponse,
)

from app.services.location_service import (
    resolve_gps_location,
    resolve_manual_location,
)


router = APIRouter(
    prefix="/location",
    tags=["Location"],
)


@router.post(
    "/resolve-gps",
    response_model=LocationResolutionResponse,
)
async def resolve_current_location(
    payload: GPSLocationRequest,
):
    try:
        result = await resolve_gps_location(
            latitude=payload.latitude,
            longitude=payload.longitude,
            accuracy_meters=payload.accuracy_meters,
        )

        return LocationResolutionResponse(
            latitude=result.latitude,
            longitude=result.longitude,
            accuracy_meters=result.accuracy_meters,
            state=result.state,
            district=result.district,
            locality=result.locality,
            display_name=result.display_name,
            source="GPS",
            verified=result.verified,
            reason=result.reason,
        )

    except httpx.HTTPStatusError as exc:
        print(
            "Location provider HTTP error:",
            exc.response.status_code,
            exc.response.text[:500],
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Location provider returned HTTP "
                f"{exc.response.status_code}."
            ),
        ) from exc

    except httpx.RequestError as exc:
        print(
            "Location provider request error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to reach the location provider."
            ),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.post(
    "/resolve-manual",
    response_model=LocationResolutionResponse,
)
async def resolve_manual(
    payload: ManualLocationRequest,
):
    try:
        result = resolve_manual_location(
            state=payload.state,
            district=payload.district,
            locality=payload.locality,
        )

        return LocationResolutionResponse(
            latitude=None,
            longitude=None,
            accuracy_meters=None,
            state=result.state,
            district=result.district,
            locality=result.locality,
            display_name=None,
            source="MANUAL",
            verified=False,
            reason=result.reason,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc