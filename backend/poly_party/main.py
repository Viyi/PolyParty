from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from poly_party.db import create_db_and_tables
from poly_party.api import users

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


# Include Routers
app.include_router(users.router, prefix="/auth", tags=["Authentication"])


@app.get("/")
def root():
    return {"message": "API is running!"}
