from typing import Annotated

EARTH_RADIUS_IN_KM: int = 6378.1


def convert_km_to_radians(km: int) -> int:
    return km / EARTH_RADIUS_IN_KM
