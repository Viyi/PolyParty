from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from poly_party.api.auth import get_session
from poly_party.models import Event, EventCreate, EventReadWithShares, Outcome, User
from poly_party.security import get_current_user

router = APIRouter()


# 1. View all Events
@router.get("/", response_model=list[Event])
def get_events(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return session.exec(select(Event)).all()


# 2. View a specific Event and all its tied Shares
@router.get("/{event_id}", response_model=EventReadWithShares)
def get_event_details(
    event_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/create", response_model=Event)
def create_event(
    event_data: EventCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1. Extract the outcomes data separately
    event_dict = event_data.model_dump(exclude={"outcomes"})

    # 2. Create the Event instance
    db_event = Event.model_validate(event_dict)

    # 3. Explicitly convert each OutcomeBase into a real Outcome table model
    if event_data.outcomes:
        db_event.outcomes = [
            Outcome.model_validate(outcome.model_dump())
            for outcome in event_data.outcomes
        ]

    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.post("/bet", response_model=Event)
def bet_event(
    event_data: Event,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
