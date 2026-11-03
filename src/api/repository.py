import json
import os
from pathlib import Path
from typing import Any

from comptalpes.model.entities import Trip, User


def db_path() -> Path:
    return Path(os.getenv("COMPTALPES_DB", "db/local-db.json"))


def _read() -> dict[str, Any]:
    path = db_path()
    if not path.is_file():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def _write(data: dict[str, Any]) -> None:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def ensure_db() -> None:
    path = db_path()
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"trips": [], "users": []}, f)


def load_trips() -> list[Trip]:
    return [Trip.model_validate(item) for item in _read().get("trips", [])]


def save_trips(trips: list[Trip]) -> None:
    data = _read()
    data["trips"] = [trip.model_dump(mode="json") for trip in trips]
    _write(data)


def load_users() -> list[User]:
    return [User.model_validate(item) for item in _read().get("users", [])]


def save_users(users: list[User]) -> None:
    data = _read()
    data["users"] = [user.model_dump(mode="json") for user in users]
    _write(data)
