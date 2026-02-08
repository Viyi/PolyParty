from datetime import datetime, timedelta

from fastapi import HTTPException
from poly_party.api import auth
from poly_party.api.events import create_event, place_bet
from poly_party.config import settings
from poly_party.models import EventCreate, OutcomeBase, User, eventType
from sqlmodel import Session, select


def create_example_users(session: Session):
    try:
        _ = auth.create_user_locally(
            username="admin", password=settings.admin_pass, admin=True, session=session
        )

        _ = auth.create_user_locally(
            username="greg", password=settings.admin_pass, admin=False, session=session
        )
    except HTTPException:
        pass


def create_example_event(session: Session):
    outcome_yes = OutcomeBase(description="Liam maintains interest.", value=0, cost=1.0)

    outcome_no = OutcomeBase(description="Liam loses interest.", value=1, cost=0.0)

    # 2. Define the EventCreate object
    example_event = EventCreate(
        title="Liam loses interest in pibble",
        description="Will liam lose interest in pibble?",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=1),
        type=eventType.SINGLETON,
        value=100,
        first_share_bonus=5.0,
        finalized=False,
        outcomes=[outcome_yes, outcome_no],
    )
    try:
        event = create_event(example_event, session=session, current_user=None)
        test_user = session.exec(select(User).where(User.username == "greg")).first()

        _ = place_bet(
            event.id, event.outcomes[0].id, 3, 1.00, session, current_user=test_user
        )

    except HTTPException:
        pass
