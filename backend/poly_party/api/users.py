from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from poly_party.db import get_session
from poly_party.models import User, UserRead
from poly_party.security import (
    get_current_user,
)
from typing import List


router = APIRouter()


@router.get("/", response_model=List[UserRead])
def get_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return session.exec(select(User)).all()
