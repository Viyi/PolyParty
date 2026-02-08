from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from poly_party.db import get_session
from poly_party.models import User, UserCreate, UserRead, Token, TokenBase, get_random_icon
from poly_party.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
import string
import random

router = APIRouter()


@router.post("/register", response_model=UserRead)
def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    admin = check_admin(current_user)

    if not admin:
        existing_token = session.exec(
            select(Token).where((Token.token == user_data.token) & (Token.used == False))
        ).first()
        if not existing_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Register token is invalid",
            )
            return
        existing_token.used = True
        session.add(existing_token)
        session.commit()
        session.refresh(existing_token)

    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        hashed_password=hashed,
        icon_url=get_random_icon(),
        balance=100,
        admin=False,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def random_token(length=4):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@router.get("/register/token", response_model=TokenBase)
def register_new_token(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    raise_not_admin(current_user)

    unique = False
    token = ""

    while not unique:
        new_token = random_token()

        existing_token = session.exec(
            select(Token).where(Token.token == new_token)
        ).first()
        print(existing_token)
        if not existing_token:
            token = new_token
            unique = True

    new_token = Token(
        token=token,
        used=False
    )
    session.add(new_token)
    session.commit()
    session.refresh(new_token)
    return new_token


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


def create_admin(username: str, password: str, session: Session):
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = hash_password(password)

    new_user = User(
        username=username,
        hashed_password=hashed,
        balance=100,
        admin=True,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def check_admin(current_user: User) -> bool:
    return current_user.admin

def raise_not_admin(current_user: User):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
