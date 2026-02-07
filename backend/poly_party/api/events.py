from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from poly_party.api.auth import get_session
from poly_party.models import (
    Event,
    EventReadWithShares,
)

router = APIRouter()


# 1. View all Events
@router.get("/", response_model=list[Event])
def get_events(session: Session = Depends(get_session)):
    return session.exec(select(Event)).all()


# 2. View a specific Event and all its tied Shares
@router.get("/{event_id}", response_model=EventReadWithShares)
def get_event_details(event_id: str, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
