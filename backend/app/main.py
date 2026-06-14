"""PenguWave backend — application entrypoint with database initialization and routes."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from .config import settings
from .database import create_db_and_tables, get_session, SessionLocal
from .seed import seed_users, seed_events
from .errors import register_error_handlers
from .routers import auth, events


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database and seed data on startup."""
    # Startup
    create_db_and_tables()
    with SessionLocal() as session:
        seed_users(session)
        seed_events(session)
    yield
    # Shutdown (nothing to do)


app = FastAPI(title="PenguWave API", version="0.1.0", lifespan=lifespan)

# CORS configuration: allow only the frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers for consistent error responses
register_error_handlers(app)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe — confirms the server is up."""
    return {"status": "ok"}
