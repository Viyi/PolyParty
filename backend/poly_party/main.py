from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from poly_party.db import create_db_and_tables
from poly_party.api import users, auth
from poly_party.models import UserCreate
from poly_party.db import get_session
from fastapi import HTTPException
from poly_party.config import settings


app = FastAPI(title="FastAPI + SQLModel Auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


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


@app.get("/")
def root():
    return {"message": "API is running!"}
