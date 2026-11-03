from fastapi.testclient import TestClient

USER_PAYLOAD = {"name": "Alice"}
TRIP_PAYLOAD = {
    "name": "Valloire",
    "start_date": "2026-01-31",
    "end_date": "2026-02-06",
}


def test_get_users_empty(client: TestClient) -> None:
    response = client.get("/user/")
    assert response.status_code == 200
    assert response.json() == []


def test_add_user(client: TestClient) -> None:
    response = client.post("/user/", json=USER_PAYLOAD)
    assert response.status_code == 200
    user = response.json()
    assert user["name"] == "Alice"
    assert user["id"]


def test_add_user_persisted(client: TestClient) -> None:
    response = client.post("/user/", json=USER_PAYLOAD)
    user_id = response.json()["id"]
    response = client.get("/user/")
    users = response.json()
    assert len(users) == 1
    assert users[0]["id"] == user_id


def test_add_user_without_name(client: TestClient) -> None:
    response = client.post("/user/", json={})
    assert response.status_code == 422


def test_update_user(client: TestClient) -> None:
    response = client.post("/user/", json=USER_PAYLOAD)
    user_id = response.json()["id"]

    response = client.patch(f"/user/{user_id}", json={"name": "Alicia"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == user_id
    assert updated["name"] == "Alicia"

    response = client.get("/user/")
    users = response.json()
    assert len(users) == 1
    assert users[0]["name"] == "Alicia"


def test_update_user_unknown_id(client: TestClient) -> None:
    response = client.patch(
        "/user/6ba7b810-9dad-11d1-80b4-00c04fd430c8", json={"name": "Alicia"}
    )
    assert response.status_code == 404


def test_delete_user(client: TestClient) -> None:
    response = client.post("/user/", json=USER_PAYLOAD)
    user_id = response.json()["id"]
    response = client.post("/user/", json={"name": "Bob"})
    bob_id = response.json()["id"]

    response = client.delete(f"/user/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

    users = client.get("/user/").json()
    assert len(users) == 1
    assert users[0]["id"] == bob_id


def test_delete_user_unknown_id(client: TestClient) -> None:
    response = client.delete("/user/6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    assert response.status_code == 404


def test_users_and_trips_coexist(client: TestClient) -> None:
    client.post("/user/", json=USER_PAYLOAD)
    client.post("/trip/", json=TRIP_PAYLOAD)
    assert len(client.get("/user/").json()) == 1
    assert len(client.get("/trip/").json()) == 1

    client.post("/user/", json={"name": "Bob"})
    assert len(client.get("/trip/").json()) == 1
    assert len(client.get("/user/").json()) == 2
