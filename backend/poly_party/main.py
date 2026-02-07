from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from poly_party.api import auth, events, users
from poly_party.config import settings
from poly_party.db import create_db_and_tables, get_session

app = FastAPI(title="FastAPI + SQLModel Auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database initialization
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    session = next(get_session())

    try:
        auth.create_admin(
            username="admin", password=settings.admin_pass, session=session
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
