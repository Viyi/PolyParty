from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from poly_party.db import get_session
from poly_party.models import User, UserRead, UserReadWithShares
from poly_party.security import (
    get_current_user,
)

router = APIRouter()


@router.get("/", response_model=List[UserRead])
def get_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return session.exec(select(User)).all()


# 3. View a specific User and all their tied Shares
@router.get("/{user_id}/shares", response_model=UserReadWithShares)
def get_user_shares(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/current", response_model=UserReadWithShares)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return current_user
