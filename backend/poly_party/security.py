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
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


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


def decode_jwt_and_get_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session), raise_exception=True) -> User:
    try:
        payload = jwt.decode(token, settings.secret_phrase, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None and raise_exception:
            raise HTTPException(status_code=401, detail="Invalid token")
        elif username is None and not raise_exception:
            return None
    except:
        if raise_exception:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        else:
            return None

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    return decode_jwt_and_get_user(token, session)

def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional), session: Session = Depends(get_session)
) -> User | None:
    if not token:
        return None
    return decode_jwt_and_get_user(token, session, raise_exception=False)