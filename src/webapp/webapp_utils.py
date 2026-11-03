from uuid import UUID

import requests

from comptalpes.model.entities import Trip, User


def get_trips(url: str) -> list[Trip] | None:
    response = requests.get(f"{url}/trip/", timeout=5)
    if response.ok:
        return [Trip.model_validate(item) for item in response.json()]
    else:
        response.raise_for_status()


def get_trip(url: str, trip_id: UUID) -> Trip | None:
    response = requests.get(f"{url}/trips/{trip_id}", timeout=5)
    if response.ok:
        return Trip.model_validate(response.json())
    else:
        response.raise_for_status()


def get_users(url: str) -> list[User] | None:
    response = requests.get(f"{url}/user/", timeout=5)
    if response.ok:
        return [User.model_validate(item) for item in response.json()]
    else:
        response.raise_for_status()
