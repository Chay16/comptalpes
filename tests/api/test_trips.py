import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_get_trips(client: TestClient) -> None:
    response = client.get("/trips/")
    assert response.status_code == 200
    trips = response.json()
    assert trips[0]["name"] == "Valloire"


def test_add_trip(client: TestClient) -> None:
    response = client.post(
        "/trips/",
        json={
            "name": "Valloire",
            "start_date": "2026-01-31",
            "end_date": "2026-02-06",
        },
    )
    assert response.status_code == 200
    trip = response.json()
    assert trip["name"] == "Valloire"
    assert trip["id"]
    assert trip["currency"] == "EUR"


def test_add_trip_invalid_dates(client: TestClient) -> None:
    response = client.post(
        "/trips/",
        json={
            "name": "Valloire",
            "start_date": "2026-02-06",
            "end_date": "2026-02-06",
        },
    )
    assert response.status_code == 422


def test_add_trip_incomplete_payload(client: TestClient) -> None:
    response = client.post("/trips/", json={"name": "Valloire"})
    assert response.status_code == 422
