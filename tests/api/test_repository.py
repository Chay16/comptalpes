import json
import shutil
from decimal import Decimal
from datetime import date
from pathlib import Path

import pytest

from api.repository import db_path, load_trips, save_trips
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
