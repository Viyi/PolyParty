import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

# --- 1. ENUMS ---


class eventType(str, Enum):
    OVER_UNDER = "over/under"
    SINGLETON = "singleton"
    MULTIPLE_CHOICE = "multiple-choice"


# --- 2. OUTCOME MODELS ---


class OutcomeBase(SQLModel):
    description: str
    value: int
    cost: float = Field(default=0.0)
    event_id: Optional[str] = Field(default=None, foreign_key="event.id")


class Outcome(OutcomeBase, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    # Relationship back to the Event
    event: "Event" = Relationship(back_populates="outcomes")


class OutcomeRead(OutcomeBase):
    id: str


# --- 3. USER MODELS ---


def get_random_icon():
    random_seed = uuid.uuid4().hex
    return f"https://api.dicebear.com/9.x/bottts/svg?seed={random_seed}"


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    balance: float = Field(default=100.0)
    # default_factory calls the function every time a new User is initialized
    icon_url: str = Field(default=get_random_icon())


class User(UserBase, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    hashed_password: str
    admin: bool = Field(default=False)

    # Relationships
    shares: List["Share"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: str


# --- 4. EVENT MODELS ---


class EventBase(SQLModel):
    title: str
    start_time: datetime
    end_time: datetime
    type: eventType
    value: int
    first_share_bonus: float = Field(default=0.0)
    finalized: bool = Field(default=False)


class Event(EventBase, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    shares: List["Share"] = Relationship(back_populates="event")
    outcomes: List["Outcome"] = Relationship(back_populates="event")


class EventCreate(EventBase):
    outcomes: List[OutcomeBase]


# --- 5. SHARE MODELS ---


class ShareBase(SQLModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    value: int
    wager: float
    event_id: str = Field(foreign_key="event.id")
    user_id: str = Field(foreign_key="user.id")


class Share(ShareBase, table=True):
    # Relationships
    event: Event = Relationship(back_populates="shares")
    user: User = Relationship(back_populates="shares")


class ShareRead(ShareBase):
    pass


# --- 6. NESTED READ SCHEMAS (For API Responses) ---


class UserReadWithShares(UserRead):
    shares: List[ShareRead] = []


class EventReadWithShares(EventBase):
    id: str
    outcomes: List[OutcomeRead] = []
    shares: List[ShareRead] = []


# --- 7. FINALIZATION ---
# This fixes the "not fully defined" errors by resolving string references
User.model_rebuild()
Event.model_rebuild()
Share.model_rebuild()
Outcome.model_rebuild()
UserReadWithShares.model_rebuild()
EventReadWithShares.model_rebuild()
