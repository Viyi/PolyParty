from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from poly_party.db import get_session
from poly_party.models import User
from fastapi.security import OAuth2PasswordBearer
from poly_party.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # pwdlib handles the salt and comparison internally
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_phrase, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(token, settings.secret_phrase, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
