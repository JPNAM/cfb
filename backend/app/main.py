from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import engine
from .models import Base
from .routers import coaches, meta, roster, score, system_states

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*" if settings.frontend_url is None else settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(meta.router)
app.include_router(system_states.router)
app.include_router(roster.router)
app.include_router(score.router)
app.include_router(coaches.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "message": "NFL lineup cohesion API"}

