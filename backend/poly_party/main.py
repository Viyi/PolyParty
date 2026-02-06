from fastapi import FastAPI
from poly_party.db import create_db_and_tables
from poly_party.api import users

app = FastAPI(title="FastAPI + SQLModel Auth")


# Database initialization
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Include Routers
app.include_router(users.router, prefix="/auth", tags=["Authentication"])


@app.get("/")
def root():
    return {"message": "API is running!"}
