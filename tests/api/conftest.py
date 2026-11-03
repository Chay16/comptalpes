import pytest
from fastapi.testclient import TestClient

from api.main import app

TRIP_PAYLOAD = {
    "name": "Valloire",
    "start_date": "2026-01-31",
    "end_date": "2026-02-06",
}


@pytest.fixture
def db_file(tmp_path, monkeypatch) -> str:
    path = tmp_path / "db.json"
    monkeypatch.setenv("COMPTALPES_DB", str(path))
    yield str(path)
    for file in tmp_path.glob("db.json*"):
        file.unlink()


@pytest.fixture
def client(db_file: str) -> TestClient:
    return TestClient(app)


@pytest.fixture
def client_and_trip(client: TestClient) -> tuple[TestClient, str]:
    response = client.post("/trip/", json=TRIP_PAYLOAD)
    assert response.status_code == 200
    return client, response.json()["id"]
