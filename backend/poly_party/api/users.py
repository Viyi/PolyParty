from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from poly_party.db import get_session
from poly_party.models import User, UserCreate, UserRead
from poly_party.security import hash_password, verify_password

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
def login(user_data: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_data.username)).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return {"message": "Login successful", "balance": user.balance}
