from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

# --- 1. ENUMS AND CONSTANTS ---


class eventType(str, Enum):
    OVER_UNDER = "over/under"
    SINGLETON = "singleton"
    MULTIPLE_CHOICE = "multiple-choice"


# --- 2. USER MODELS ---


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    balance: float = Field(default=100.0)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    admin: Optional[bool] = Field(default=False)

    shares: List["Share"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


# --- 3. EVENT MODELS ---


class EventBase(SQLModel):
    id: str = Field(primary_key=True)
    title: str
    start_time: datetime
    end_time: datetime
    type: eventType
    value: int
    first_share_bonus: float = Field(default=0.0)
    finalized: bool = Field(default=False)


class Event(EventBase, table=True):
    # Relationship to the database table
    shares: List["Share"] = Relationship(back_populates="event")


# --- 4. SHARE MODELS ---


class ShareBase(SQLModel):
    id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    value: int
    wager: float
    event_id: str = Field(foreign_key="event.id")
    user_id: int = Field(foreign_key="user.id")


class Share(ShareBase, table=True):
    event: Event = Relationship(back_populates="shares")
    user: User = Relationship(back_populates="shares")


# --- 5. READ SCHEMAS (With Relationships) ---
# These are used as 'response_model' in your routes to show nested data


class ShareRead(ShareBase):
    """Simple share view without nested user/event to prevent recursion."""

    pass


class UserReadWithShares(UserRead):
    shares: List[ShareRead] = []


class EventReadWithShares(EventBase):
    shares: List[ShareRead] = []
