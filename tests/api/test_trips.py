from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app

TRIP_PAYLOAD = {
    "name": "Valloire",
    "start_date": "2026-01-31",
    "end_date": "2026-02-06",
}


def test_lifespan_creates_db_file(db_file: str) -> None:
    assert not Path(db_file).exists()
    with TestClient(app) as client:
        response = client.get("/trips/")
    assert response.status_code == 200
    assert Path(db_file).is_file()


def test_get_trips_empty(client: TestClient) -> None:
    response = client.get("/trips/")
    assert response.status_code == 200
    assert response.json() == []


def test_add_trip(client: TestClient) -> None:
    response = client.post("/trips/", json=TRIP_PAYLOAD)
    assert response.status_code == 200
    trip = response.json()
    assert trip["name"] == "Valloire"
    assert trip["id"]
    assert trip["currency"] == "EUR"


def test_add_trip_persisted(client_and_trip: tuple[TestClient, str]) -> None:
    client, trip_id = client_and_trip
    response = client.get("/trips/")
    assert response.status_code == 200
    trips = response.json()
    assert len(trips) == 1
    assert trips[0]["id"] == trip_id


def test_get_trip_by_id(client_and_trip: tuple[TestClient, str]) -> None:
    client, trip_id = client_and_trip
    response = client.get(f"/trips/{trip_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Valloire"


def test_get_trip_unknown_id(client: TestClient) -> None:
    response = client.get("/trips/6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    assert response.status_code == 404


def test_add_trip_invalid_dates(client: TestClient) -> None:
    payload = {**TRIP_PAYLOAD, "start_date": "2026-02-06"}
    response = client.post("/trips/", json=payload)
    assert response.status_code == 422


def test_add_trip_incomplete_payload(client: TestClient) -> None:
    response = client.post("/trips/", json={"name": "Valloire"})
    assert response.status_code == 422


def test_add_trip_with_members(client: TestClient) -> None:
    payload = {
        **TRIP_PAYLOAD,
        "members": [
            {
                "name": "Alice",
                "arrival_date": "2026-01-31",
                "departure_date": "2026-02-06",
            }
        ],
    }
    response = client.post("/trips/", json=payload)
    assert response.status_code == 200
    members = response.json()["members"]
    assert len(members) == 1
    assert members[0]["user"]["name"] == "Alice"


def test_add_trip_member_out_of_range(client: TestClient) -> None:
    payload = {
        **TRIP_PAYLOAD,
        "members": [
            {
                "name": "Alice",
                "arrival_date": "2026-01-30",
                "departure_date": "2026-02-06",
            }
        ],
    }
    response = client.post("/trips/", json=payload)
    assert response.status_code == 422


def test_add_member(client_and_trip: tuple[TestClient, str]) -> None:
    client, trip_id = client_and_trip
    payload = {
        "name": "Bob",
        "arrival_date": "2026-02-01",
        "departure_date": "2026-02-05",
    }
    response = client.post(f"/trips/{trip_id}/members/", json=payload)
    assert response.status_code == 200
    members = response.json()["members"]
    assert len(members) == 1
    assert members[0]["user"]["name"] == "Bob"

    response = client.get(f"/trips/{trip_id}")
    assert len(response.json()["members"]) == 1


def test_add_member_invalid_dates(client_and_trip: tuple[TestClient, str]) -> None:
    client, trip_id = client_and_trip
    payload = {
        "name": "Bob",
        "arrival_date": "2026-02-05",
        "departure_date": "2026-02-01",
    }
    response = client.post(f"/trips/{trip_id}/members/", json=payload)
    assert response.status_code == 422


def test_add_member_unknown_trip(client: TestClient) -> None:
    payload = {
        "name": "Bob",
        "arrival_date": "2026-02-01",
        "departure_date": "2026-02-05",
    }
    response = client.post(
        "/trips/6ba7b810-9dad-11d1-80b4-00c04fd430c8/members/", json=payload
    )
    assert response.status_code == 404


def test_add_expense(client_and_trip: tuple[TestClient, str]) -> None:
    client, trip_id = client_and_trip
    response = client.post(
        f"/trips/{trip_id}/expenses/",
        json={"description": "Raclette", "amount": "45.5"},
    )
    assert response.status_code == 200
    expense = response.json()
    assert expense["amount"] == "45.50"
    assert expense["expense_date"] == date.today().isoformat()
    assert expense["category"]["name"] == "Divers"

    response = client.get(f"/trips/{trip_id}")
    expenses = response.json()["expenses"]
    assert len(expenses) == 1
    assert expenses[0]["id"] == expense["id"]


def test_add_expense_with_split_type(client_and_trip: tuple[TestClient, str]) -> None:
    client, trip_id = client_and_trip
    response = client.post(
        f"/trips/{trip_id}/expenses/",
        json={
            "description": "Chalet",
            "amount": "1000",
            "expense_date": "2026-01-31",
            "category": "house",
            "split_type": "by_nights",
        },
    )
    assert response.status_code == 200
    expense = response.json()
    assert expense["category"]["name"] == "house"
    assert expense["split_type_override"] == "by_nights"


def test_add_expense_non_positive_amount(
    client_and_trip: tuple[TestClient, str],
) -> None:
    client, trip_id = client_and_trip
    response = client.post(
        f"/trips/{trip_id}/expenses/",
        json={"description": "Raclette", "amount": "0"},
    )
    assert response.status_code == 422


def test_add_expense_unknown_trip(client: TestClient) -> None:
    response = client.post(
        "/trips/6ba7b810-9dad-11d1-80b4-00c04fd430c8/expenses/",
        json={"description": "Raclette", "amount": "45.5"},
    )
    assert response.status_code == 404


def test_update_expense(client_and_trip: tuple[TestClient, str]) -> None:
    client, trip_id = client_and_trip
    response = client.post(
        f"/trips/{trip_id}/expenses/",
        json={"description": "Raclette", "amount": "45.5"},
    )
    expense_id = response.json()["id"]

    response = client.patch(
        f"/trips/{trip_id}/expenses/{expense_id}",
        json={"amount": "50", "category": "food"},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == expense_id
    assert updated["amount"] == "50.00"
    assert updated["category"]["name"] == "food"
    assert updated["description"] == "Raclette"

    response = client.get(f"/trips/{trip_id}")
    expenses = response.json()["expenses"]
    assert len(expenses) == 1
    assert expenses[0]["amount"] == "50.00"


def test_update_expense_unknown_expense(
    client_and_trip: tuple[TestClient, str],
) -> None:
    client, trip_id = client_and_trip
    response = client.patch(
        f"/trips/{trip_id}/expenses/6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        json={"amount": "50"},
    )
    assert response.status_code == 404


def test_update_expense_unknown_trip(client: TestClient) -> None:
    response = client.patch(
        "/trips/6ba7b810-9dad-11d1-80b4-00c04fd430c8/expenses/"
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        json={"amount": "50"},
    )
    assert response.status_code == 404
