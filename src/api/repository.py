import json
import os
from pathlib import Path

from comptalpes.model.entities import Trip


def db_path() -> Path:
    return Path(os.getenv("COMPTALPES_DB", "db/local-db.json"))


def ensure_db() -> None:
    path = db_path()
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"trips": []}, f)


def load_trips() -> list[Trip]:
    path = db_path()
    if not path.is_file():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    return [Trip.model_validate(item) for item in data.get("trips", [])]


def save_trips(trips: list[Trip]) -> None:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"trips": [trip.model_dump(mode="json") for trip in trips]}
    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)
