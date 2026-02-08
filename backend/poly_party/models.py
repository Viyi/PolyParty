import uuid
from datetime import datetime
from enum import Enum

from pydantic import model_validator
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
    cost: float = Field(default=0.50)
    event_id: str | None = Field(default=None, foreign_key="event.id")


class Outcome(OutcomeBase, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    # Relationship back to the Event
    event: "Event" = Relationship(back_populates="outcomes")
    shares: list["Share"] = Relationship(back_populates="outcome")


class OutcomeRead(OutcomeBase):
    id: str


# --- 3. USER MODELS ---


class TokenBase(SQLModel):
    token: str = Field(index=True, unique=True)
    used: bool = Field(default=False)


class Token(TokenBase, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    token: str = Field(index=True, unique=True)
    used: bool = Field(default=False)


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    balance: float = Field(default=100.0)
    icon_url: str | None = Field(default=None)  # Start as None

    @model_validator(mode="after")
    def set_default_icon(self) -> "UserBase":
        if not self.icon_url:
            # You can use the username as the seed so the icon is consistent
            self.icon_url = (
                f"https://api.dicebear.com/9.x/bottts/svg?seed={self.username}"
            )
        return self


class User(UserBase, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
    hashed_password: str
    admin: bool = Field(default=False)

    # Relationships
    shares: list["Share"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str
    token: str


class UserRead(UserBase):
    id: str


class IconCreate(SQLModel):
    icon_url: str
    random: bool


# --- 4. EVENT MODELS ---


class EventBase(SQLModel):
    title: str
    description: str
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

    shares: list["Share"] = Relationship(back_populates="event")
    outcomes: list["Outcome"] = Relationship(back_populates="event")


class EventCreate(EventBase):
    outcomes: list[OutcomeBase]


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
    outcome_id: str = Field(foreign_key="outcome.id")


class Share(ShareBase, table=True):
    # Relationships
    event: Event = Relationship(back_populates="shares")
    outcome: Outcome = Relationship(back_populates="shares")
    user: User = Relationship(back_populates="shares")


class ShareRead(ShareBase):
    pass


# --- 6. NESTED READ SCHEMAS (For API Responses) ---


class UserReadWithShares(UserRead):
    admin: bool
    shares: list[ShareRead] = []


class EventReadWithShares(EventBase):
    id: str
    outcomes: list[OutcomeRead] = []
    shares: list[ShareRead] = []


# --- 7. FINALIZATION ---
# This fixes the "not fully defined" errors by resolving string references
User.model_rebuild()
Event.model_rebuild()
Share.model_rebuild()
Outcome.model_rebuild()
UserReadWithShares.model_rebuild()
EventReadWithShares.model_rebuild()
