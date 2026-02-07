import uuid
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException
from poly_party.db import get_session
from poly_party.models import (
    Event,
    EventCreate,
    EventReadWithShares,
    Outcome,
    Share,
    ShareRead,
    User,
)
from poly_party.security import get_current_user
from sqlmodel import Session, select

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


@router.post("/bet", response_model=List[ShareRead])
def place_bet(
    event_id: int,
    quantity: int = Body(..., embed=True),
    price_per_share: float = Body(..., embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[ShareRead]:
    db_event: Event | None = session.get(Event, event_id)
    if not db_event or not db_event.id:
        raise HTTPException(status_code=404, detail="Event not found")

    if db_event and db_event.finalized:
        raise HTTPException(status_code=400, detail="Event is already finalized")

    # 2. Check User Balance
    total_cost = quantity * price_per_share
    if current_user.balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # 3. Deduct balance from user
    current_user.balance -= total_cost
    session.add(current_user)

    # 4. Create n number of Share records
    new_shares: list[Share] = []
    for _ in range(quantity):
        share = Share(
            id=str(uuid.uuid4()),  # Generating unique IDs for each share
            value=db_event.value,  # Inheriting value logic from the event
            wager=price_per_share,
            event_id=db_event.id,
            user_id=current_user.id,
            timestamp=datetime.utcnow(),
        )
        session.add(share)
        new_shares.append(share)

    # 5. Commit the transaction
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Transaction failed")

    # Refresh to get the final state
    for share in new_shares:
        session.refresh(share)

    return new_shares
