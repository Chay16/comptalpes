from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

from comptalpes.model.entities import Trip

router = APIRouter()


class TripPayload(BaseModel):
    name: str
    start_date: date
    end_date: date
    currency: str = "EUR"


def build_trip(payload: TripPayload) -> Trip:
    return Trip(
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        currency=payload.currency,
    )


@router.get("/trips/", tags=["trips"])
def get_trips():
    trip = build_trip(
        TripPayload(name="Valloire", start_date="2026-01-31", end_date="2026-02-06")
    )
    return [trip]


@router.post("/trips/", tags=["trips"])
def add_trip(payload: TripPayload):
    return build_trip(payload)
