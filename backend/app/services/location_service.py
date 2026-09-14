from dataclasses import dataclass

import httpx


NOMINATIM_REVERSE_URL = (
    "https://nominatim.openstreetmap.org/reverse"
)

NOMINATIM_USER_AGENT = (
    "SocietalInnovationPlatform/1.0 "
    "(development demo)"
)


# ============================================================
# Resolved Location
# ============================================================

@dataclass
class ResolvedLocation:
    latitude: float | None
    longitude: float | None
    accuracy_meters: float | None

    state: str | None
    district: str | None
    locality: str | None

    display_name: str | None
    reason: str
    verified: bool


# ============================================================
# Helpers
# ============================================================

def _first_non_empty(
    *values: str | None,
) -> str | None:
    for value in values:
        if value and value.strip():
            return value.strip()

    return None


def _resolve_district(
    address: dict,
) -> str | None:
    """
    OSM address structures vary by geography.

    For India, district information can appear under
    county, state_district, district, or city_district.
    """

    return _first_non_empty(
        address.get("county"),
        address.get("state_district"),
        address.get("district"),
        address.get("city_district"),
    )


def _resolve_locality(
    address: dict,
) -> str | None:
    return _first_non_empty(
        address.get("village"),
        address.get("town"),
        address.get("city"),
        address.get("municipality"),
        address.get("suburb"),
        address.get("locality"),
        address.get("neighbourhood"),
    )


# ============================================================
# GPS Location Resolution
# ============================================================

async def resolve_gps_location(
    latitude: float,
    longitude: float,
    accuracy_meters: float | None = None,
) -> ResolvedLocation:

    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "jsonv2",
        "addressdetails": 1,
        "accept-language": "en",
        "zoom": 18,
    }

    headers = {
        "User-Agent": NOMINATIM_USER_AGENT,
        "Accept": "application/json",
    }

    timeout = httpx.Timeout(
        10.0,
        connect=5.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        headers=headers,
    ) as client:
        response = await client.get(
            NOMINATIM_REVERSE_URL,
            params=params,
        )

        response.raise_for_status()

        data = response.json()

    address = data.get("address") or {}

    state = _first_non_empty(
        address.get("state"),
    )

    district = _resolve_district(address)

    locality = _resolve_locality(address)

    display_name = data.get("display_name")

    # --------------------------------------------------------
    # Administrative resolution failed
    # --------------------------------------------------------

    if not state and not district:
        return ResolvedLocation(
            latitude=latitude,
            longitude=longitude,
            accuracy_meters=accuracy_meters,
            state=None,
            district=None,
            locality=locality,
            display_name=display_name,
            reason=(
                "GPS coordinates were received, but the "
                "administrative jurisdiction could not be resolved."
            ),
            verified=False,
        )

    # --------------------------------------------------------
    # Accuracy information
    # --------------------------------------------------------

    accuracy_note = ""

    if accuracy_meters is not None:
        accuracy_note = (
            f" GPS accuracy reported by the device: "
            f"{accuracy_meters:.1f} meters."
        )

    # --------------------------------------------------------
    # Successful resolution
    # --------------------------------------------------------

    return ResolvedLocation(
        latitude=latitude,
        longitude=longitude,
        accuracy_meters=accuracy_meters,
        state=state,
        district=district,
        locality=locality,
        display_name=display_name,
        reason=(
            "GPS coordinates were reverse-geocoded to the "
            f"detected jurisdiction.{accuracy_note}"
        ),
        verified=True,
    )


# ============================================================
# Manual Location Resolution
# ============================================================

def resolve_manual_location(
    state: str | None,
    district: str | None,
    locality: str | None = None,
) -> ResolvedLocation:

    normalized_state = (
        state.strip()
        if state and state.strip()
        else None
    )

    normalized_district = (
        district.strip()
        if district and district.strip()
        else None
    )

    normalized_locality = (
        locality.strip()
        if locality and locality.strip()
        else None
    )

    has_location = any(
        [
            normalized_state is not None,
            normalized_district is not None,
            normalized_locality is not None,
        ]
    )

    return ResolvedLocation(
        # Manual location does not inherently provide
        # geographic coordinates.
        latitude=None,
        longitude=None,
        accuracy_meters=None,
        state=normalized_state,
        district=normalized_district,
        locality=normalized_locality,
        display_name=None,
        reason=(
            "Location supplied manually by the citizen."
            if has_location
            else "No location was provided."
        ),
        verified=False,
    )