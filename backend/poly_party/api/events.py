from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException
from poly_party.db import get_session
from poly_party.models import (
    Event,
    EventCreate,
    EventReadWithShares,
    Outcome,
    Share,
    User,
)
from poly_party.security import get_current_user
from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

router = APIRouter()


@router.get("/", response_model=list[EventReadWithShares])  # 1. Update response model
def get_events(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = select(Event).options(
        selectinload(Event.shares), selectinload(Event.outcomes)
    )
    return session.exec(statement).all()


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
    existing_event = session.exec(
        select(Event).where(Event.title == event_data.title)
    ).first()
    if existing_event:
        raise HTTPException(
            status_code=400, detail="Event of that name already registered."
        )

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


@router.post("/bet", response_model=list[Share])
def place_bet(
    event_id: str,
    outcome_id: str,
    quantity: int = Body(..., embed=True),
    expected_price: float = Body(..., embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[Share]:
    # 1. Validation
    db_event = session.get(Event, event_id)
    if not db_event or db_event.finalized:
        raise HTTPException(status_code=400, detail="Event unavailable or finalized")

    db_outcome = session.get(Outcome, outcome_id)
    if not db_outcome or db_outcome.event_id != event_id:
        raise HTTPException(status_code=404, detail="Outcome not found")

    # 2. Calculate the actual cost using the scaled model
    # We get the list of prices for the quantity requested
    prices = calculate_outcome_costs(quantity, db_outcome, db_event, session)
    total_cost = sum(prices)
    final_share_price = prices[-1]

    # Slippage check: if the last share is more expensive than the user expected, block the trade
    if final_share_price > expected_price + 0.01:  # Small buffer for float math
        raise HTTPException(status_code=400, detail="Price moved too much (slippage)")

    if current_user.balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # 3. Deduct balance and create shares
    current_user.balance -= total_cost
    session.add(current_user)

    new_shares: list[Share] = []
    for price in prices:
        share = Share(
            value=db_event.value,
            outcome_id=outcome_id,
            wager=price,  # Store the actual price paid for THIS specific share
            event_id=db_event.id,
            user_id=current_user.id,
        )
        session.add(share)
        new_shares.append(share)

    # 4. UPDATE ALL OUTCOMES (The new percentages)
    # We must commit or flush here so the next calculation sees the new shares
    session.flush()

    for outcome in db_event.outcomes:
        # Calculate what the NEXT single share would cost for this outcome
        # This updates the 'cost' field used by the UI to show the current price
        next_price_list = calculate_outcome_costs(1, outcome, db_event, session)
        outcome.cost = next_price_list[0]
        session.add(outcome)

    # 5. Finalize
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Transaction failed")

    # Optional: Broadcast new outcome costs via WebSocket here
    # await manager.broadcast({"type": "PRICE_UPDATE", "event_id": event_id})

    for share in new_shares:
        session.refresh(share)

    return new_shares


@router.post("/bet/cost", response_model=list[float])
def get_outcome_costs(
    num_shares: int,
    event_id: str,
    outcome_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1. Fetch the Event
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. Fetch the Outcome
    # It's good practice to ensure the outcome actually belongs to the event
    outcome = session.get(Outcome, outcome_id)
    if not outcome or outcome.event_id != event_id:
        raise HTTPException(status_code=404, detail="Outcome not found for this event")

    # 3. Calculate the step-by-step prices
    prices = calculate_outcome_costs(num_shares, outcome, event, session)

    return prices


def calculate_outcome_costs(
    num_shares: int, selected_outcome: Outcome, event: Event, session: Session
):
    # 1. Get current total shares for this specific outcome
    # We sum the 'value' (number of shares per record)
    current_outcome_shares: int | Literal[0] = (
        session.exec(
            select(func.sum(Share.value)).where(Share.outcome_id == selected_outcome.id)
        ).one()
        or 0
    )

    # 2. Get current total shares for the entire event
    total_event_shares = (
        session.exec(
            select(func.sum(Share.value)).where(Share.event_id == event.id)
        ).one()
        or 0
    )

    total_cost = 0.0

    # We iterate to simulate price slippage
    # For every 1 share purchased, the price for the NEXT one goes up
    temp_outcome_shares = current_outcome_shares
    temp_total_event_shares = total_event_shares

    prices: list[float] = []
    for _ in range(num_shares):
        # Prevent division by zero if it's the first share ever
        if temp_total_event_shares == 0:
            # Default to an even split price if market is empty
            current_price = 1.0 / len(event.outcomes) if event.outcomes else 0.5
        else:
            current_price = temp_outcome_shares / temp_total_event_shares

        # Clamp price between a small minimum and $1.00
        current_price = max(0.01, min(current_price, 0.99))

        prices.append(current_price)
        total_cost += current_price

        # Simulate the purchase for the next iteration
        temp_outcome_shares += 1
        temp_total_event_shares += 1

    return prices
