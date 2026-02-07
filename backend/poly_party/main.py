from fastapi import FastAPI, HTTPException

from poly_party.api import auth, events, users
from poly_party.config import settings
from poly_party.db import create_db_and_tables, get_session
from poly_party.models import UserCreate

app = FastAPI(title="FastAPI + SQLModel Auth")


# Database initialization
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    session = next(get_session())

    try:
        auth.register_user(
            UserCreate(username="admin", password=settings.admin_pass), session=session
        )
    except HTTPException:
        pass


# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(events.router, prefix="/events", tags=["Events"])


@app.get("/")
def root():
    return {"message": "API is running!"}
