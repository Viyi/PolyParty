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
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationship back to the Event
    event: "Event" = Relationship(back_populates="outcomes")


class OutcomeRead(OutcomeBase):
    id: int


# --- 3. USER MODELS ---


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    balance: float = Field(default=100.0)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    admin: bool = Field(default=False)

    # Relationships
    shares: List["Share"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


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
    id: Optional[int] = Field(default=None, primary_key=True)

    shares: List["Share"] = Relationship(back_populates="event")
    outcomes: List["Outcome"] = Relationship(back_populates="event")


class EventCreate(EventBase):
    outcomes: List[OutcomeBase]


# --- 5. SHARE MODELS ---


class ShareBase(SQLModel):
    id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    value: int
    wager: float
    event_id: str = Field(foreign_key="event.id")
    user_id: int = Field(foreign_key="user.id")


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
    id: Optional[int] = Field(default=None, primary_key=True)
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
