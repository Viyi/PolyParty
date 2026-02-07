from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from poly_party.api.auth import get_session
from poly_party.main import app
from poly_party.models import Event, User, eventType
from poly_party.security import get_current_user
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# --- SETUP ---


@pytest.fixture(name="session")
def session_fixture():
    # Use StaticPool to maintain the connection in memory across the test
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_current_user_override():
        return User(username="testuser", id=1, hashed_password="")

    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)
    app.dependency_overrides.clear()


# --- TESTS ---


# 1. Test GET all events
def test_get_events(client: TestClient, session: Session):
    event = Event(
        id=1,
        title="Test Event",
        type=eventType.OVER_UNDER,
        start_time=datetime.fromisoformat("2026-01-01T10:00:00"),
        end_time=datetime.fromisoformat("2026-01-01T12:00:00"),
        value=100,
    )
    session.add(event)
    session.commit()

    response = client.get("/events/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Event"


# 2. Test GET specific event details
def test_get_event_details(client: TestClient, session: Session):
    # Use an integer ID to match your Event model (Optional[int])
    event_id = 123
    event = Event(
        id=event_id,
        title="Specific Event",
        type=eventType.SINGLETON,
        start_time=datetime.fromisoformat("2026-01-01T10:00:00"),
        end_time=datetime.fromisoformat("2026-01-01T12:00:00"),
        value=50,
    )
    session.add(event)
    session.commit()

    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data["id"] == event_id
    assert "outcomes" in data
    assert data["title"] == "Specific Event"


def test_get_event_not_found(client: TestClient):
    # Testing a 404 response
    response = client.get("/events/999")
    assert response.status_code == 404


# 3. Test POST create event
def test_create_event(client: TestClient):
    # In JSON payloads (HTTP), using strings is CORRECT.
    # FastAPI/Pydantic will handle the conversion to datetime for you.
    payload = {
        "title": "Super Bowl 2026",
        "start_time": "2026-02-08T23:00:00",
        "end_time": "2026-02-09T04:00:00",
        "type": "over/under",
        "value": 50,
        "outcomes": [
            {"description": "Over 45.5", "value": 1},
            {"description": "Under 45.5", "value": 0},
        ],
    }

    response = client.post("/events/create", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Super Bowl 2026"
    assert data["id"] is not None
    # Verify that the response includes fields from EventBase
    assert data["type"] == "over/under"
