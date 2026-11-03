import json
import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from api.repository import (
    db_path,
    ensure_db,
    load_trips,
    load_users,
    save_trips,
    save_users,
)
from comptalpes.model.entities import (
    Expense,
    ExpenseCategory,
    Trip,
    TripMember,
    User,
)


def build_trip() -> Trip:
    member = TripMember(
        user=User(name="Alice"),
        arrival_date=date(2026, 1, 31),
        departure_date=date(2026, 2, 6),
    )
    expense = Expense(
        description="Fundue",
        amount=Decimal("100.00"),
        expense_date=date(2026, 2, 1),
        category=ExpenseCategory(name="Restaurant"),
    )
    return Trip(
        name="Valloire",
        start_date=date(2026, 1, 31),
        end_date=date(2026, 2, 6),
        members=[member],
        expenses=[expense],
    )


def test_load_missing_file(db_file: str) -> None:
    assert load_trips() == []


def test_save_load_round_trip(db_file: str) -> None:
    trip = build_trip()
    save_trips([trip])
    loaded = load_trips()
    assert len(loaded) == 1
    assert loaded[0].id == trip.id
    assert loaded[0].members[0].id == trip.members[0].id
    assert loaded[0].expenses[0].id == trip.expenses[0].id
    assert loaded[0].expenses[0].amount == trip.expenses[0].amount


def test_save_creates_parent_directory(tmp_path, monkeypatch) -> None:
    path = tmp_path / "sub" / "dir" / "db.json"
    monkeypatch.setenv("COMPTALPES_DB", str(path))
    save_trips([build_trip()])
    assert path.is_file()
    shutil.rmtree(tmp_path / "sub")


def test_load_invalid_json(db_file: str) -> None:
    with open(db_file, "w", encoding="utf-8") as f:
        f.write("{invalid")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_trips()


def test_load_missing_trips_key(db_file: str) -> None:
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump({}, f)
    assert load_trips() == []


def test_db_path_uses_env(db_file: str) -> None:
    assert db_path() == Path(db_file)


def test_ensure_db_creates_file(db_file: str) -> None:
    ensure_db()
    assert Path(db_file).is_file()
    assert json.loads(Path(db_file).read_text(encoding="utf-8")) == {
        "trip": {},
        "users": [],
    }


def test_ensure_db_creates_parent_directory(tmp_path, monkeypatch) -> None:
    path = tmp_path / "missing" / "db.json"
    monkeypatch.setenv("COMPTALPES_DB", str(path))
    ensure_db()
    assert path.is_file()


def test_ensure_db_does_not_overwrite(db_file: str) -> None:
    save_trips([build_trip()])
    ensure_db()
    assert len(load_trips()) == 1


def test_save_trips_keeps_users(db_file: str) -> None:
    save_users([User(name="Alice")])
    save_trips([build_trip()])
    assert len(load_users()) == 1
    assert len(load_trips()) == 1


def test_save_users_keeps_trips(db_file: str) -> None:
    save_trips([build_trip()])
    save_users([User(name="Alice")])
    assert len(load_trips()) == 1
    assert len(load_users()) == 1


def test_load_users_missing_file(db_file: str) -> None:
    assert load_users() == []


def test_save_load_users_round_trip(db_file: str) -> None:
    alice = User(name="Alice")
    bob = User(name="Bob")
    save_users([alice, bob])
    loaded = load_users()
    assert [user.id for user in loaded] == [alice.id, bob.id]
    assert [user.name for user in loaded] == ["Alice", "Bob"]
