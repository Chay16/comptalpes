from uuid import UUID

import requests

from comptalpes.model.entities import Trip


def get_trips(url: str) -> list[Trip]:
    try:
        response = requests.get(f"{url}/trips/", timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return []
    return [Trip.model_validate(item) for item in response.json()]


def get_trip(url: str, trip_id: UUID) -> Trip | None:
    try:
        response = requests.get(f"{url}/trips/{trip_id}", timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return None
    return Trip.model_validate(response.json())
