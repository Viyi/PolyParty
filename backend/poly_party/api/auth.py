from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from poly_party.db import get_session
from poly_party.models import User, UserCreate, UserRead
from poly_party.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from sqlmodel import Session, select

router = APIRouter()


@router.post("/register", response_model=UserRead)
def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    raise_not_admin(current_user)

    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        hashed_password=hashed,
        icon_url=user_data.icon_url,
        balance=100,
        admin=False,
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

    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}


def create_user_locally(username: str, password: str, admin: bool, session: Session):
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = hash_password(password)

    new_user = User(
        username=username,
        hashed_password=hashed,
        balance=100,
        admin=admin,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def raise_not_admin(current_user: User):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
