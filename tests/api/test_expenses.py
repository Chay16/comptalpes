from datetime import date

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_get_expenses(client: TestClient) -> None:
    response = client.get("/expenses/")
    assert response.status_code == 200
    expense = response.json()[0]
    assert expense["description"] == "Fundue"
    assert expense["category"]["name"] == "Restaurant"


def test_add_expense_defaults(client: TestClient) -> None:
    response = client.post(
        "/expenses/",
        json={"description": "Raclette", "amount": "45.5"},
    )
    assert response.status_code == 200
    expense = response.json()
    assert expense["amount"] == "45.50"
    assert expense["expense_date"] == date.today().isoformat()
    assert expense["category"]["name"] == "Divers"


def test_add_expense_with_split_type(client: TestClient) -> None:
    response = client.post(
        "/expenses/",
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


def test_add_expense_non_positive_amount(client: TestClient) -> None:
    response = client.post(
        "/expenses/",
        json={"description": "Raclette", "amount": "0"},
    )
    assert response.status_code == 422


def test_update_expense(client: TestClient) -> None:
    response = client.patch(
        "/expenses/",
        json={"description": "Raclette", "amount": "50"},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == "50.00"
