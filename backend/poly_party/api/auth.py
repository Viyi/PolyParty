from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from poly_party.db import get_session
from poly_party.models import User, UserCreate, UserRead
from poly_party.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/register", response_model=UserRead)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        hashed_password=hashed,
        balance=100,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post("/login")
def login(
    # Change user_data to form_data using OAuth2PasswordRequestForm
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    # Access credentials via form_data.username and form_data.password
    user = session.exec(select(User).where(User.username == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }
