from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.repository import load_trips, load_users, save_trips
from comptalpes.model.entities import (
    Expense,
    ExpenseCategory,
    Trip,
    TripMember,
    User,
)
from comptalpes.model.enums import SplitType

router = APIRouter()


class TripMemberPayload(BaseModel):
    user_id: UUID
    arrival_date: date
    departure_date: date


class TripPayload(BaseModel):
    name: str
    start_date: date
    end_date: date
    currency: str = "EUR"
    members: list[TripMemberPayload] | None = None


class ExpensePayload(BaseModel):
    description: str
    amount: Decimal
    expense_date: date | None = None
    category: str = "Other"
    split_type: SplitType | None = None


class ExpenseUpdatePayload(BaseModel):
    description: str | None = None
    amount: Decimal | None = None
    expense_date: date | None = None
    category: str | None = None
    split_type: SplitType | None = None


def get_user_from_user_id(users: list[User], user_id: UUID) -> User:
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail=f"User {user_id} not found.")


def build_trip(payload: TripPayload) -> Trip:
    users = load_users()
    members = [
        TripMember(
            user=get_user_from_user_id(users, member_payload.user_id),
            arrival_date=member_payload.arrival_date,
            departure_date=member_payload.departure_date,
        )
        for member_payload in payload.members or []
    ]
    return Trip(
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        currency=payload.currency,
        members=members,
    )


def get_trip_from_trip_id(trips: list[Trip], trip_id: UUID) -> Trip:
    for trip in trips:
        if trip.id == trip_id:
            return trip
    raise HTTPException(status_code=404, detail=f"Trip {trip_id} not found.")


def get_expense(trip: Trip, expense_id: UUID) -> Expense:
    for expense in trip.expenses:
        if expense.id == expense_id:
            return expense
    raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found.")


def replace_trip(trips: list[Trip], old: Trip, **updates) -> Trip:
    updated = Trip(
        id=old.id,
        name=updates.get("name", old.name),
        start_date=updates.get("start_date", old.start_date),
        end_date=updates.get("end_date", old.end_date),
        currency=updates.get("currency", old.currency),
        members=updates.get("members", old.members),
        expenses=updates.get("expenses", old.expenses),
        transfers=updates.get("transfers", old.transfers),
    )
    trips[trips.index(old)] = updated
    save_trips(trips)
    return updated


@router.get("/trip/", tags=["trips"])
def get_trips():
    return load_trips()


@router.post("/trip/", tags=["trips"])
def add_trip(payload: TripPayload):
    trip = build_trip(payload)
    trips = load_trips()
    trips.append(trip)
    save_trips(trips)
    return trip


@router.get("/trip/{trip_id}", tags=["trips"])
def get_trip(trip_id: UUID):
    return get_trip_from_trip_id(load_trips(), trip_id)


@router.post("/trip/{trip_id}/members/", tags=["trips"])
def add_member(trip_id: UUID, payload: TripMemberPayload):
    trips = load_trips()
    trip = get_trip_from_trip_id(trips, trip_id)
    if any(member.user.id == payload.user_id for member in trip.members):
        raise HTTPException(
            status_code=409,
            detail=f"User {payload.user_id} is already a member of trip {trip_id}.",
        )
    user = get_user_from_user_id(load_users(), payload.user_id)
    member = TripMember(
        user=user,
        arrival_date=payload.arrival_date,
        departure_date=payload.departure_date,
    )
    return replace_trip(trips, trip, members=[*trip.members, member])


@router.post("/trip/{trip_id}/expenses/", tags=["trips"])
def add_expense(trip_id: UUID, payload: ExpensePayload):
    trips = load_trips()
    trip = get_trip_from_trip_id(trips, trip_id)
    expense = Expense(
        description=payload.description,
        amount=payload.amount,
        expense_date=payload.expense_date or date.today(),
        category=ExpenseCategory(name=payload.category),
        split_type_override=payload.split_type,
    )
    replace_trip(trips, trip, expenses=[*trip.expenses, expense])
    return expense


@router.patch("/trip/{trip_id}/expenses/{expense_id}", tags=["trips"])
def update_expense(trip_id: UUID, expense_id: UUID, payload: ExpenseUpdatePayload):
    trips = load_trips()
    trip = get_trip_from_trip_id(trips, trip_id)
    expense = get_expense(trip, expense_id)

    category_name = payload.category or expense.category.name
    category = ExpenseCategory(
        id=expense.category.id,
        name=category_name,
        split_type=expense.category.split_type,
    )
    updated_expense = Expense(
        id=expense.id,
        description=payload.description or expense.description,
        amount=payload.amount or expense.amount,
        expense_date=payload.expense_date or expense.expense_date,
        category=category,
        split_type_override=payload.split_type or expense.split_type_override,
        payments=expense.payments,
        shares=expense.shares,
    )

    updated_expenses = [
        updated_expense if item.id == expense_id else item for item in trip.expenses
    ]
    replace_trip(trips, trip, expenses=updated_expenses)
    return updated_expense
