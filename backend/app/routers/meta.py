from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import SeasonResponse, TeamResponse
from ..services.system_state_service import list_seasons, list_teams

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/meta/seasons", response_model=SeasonResponse)
def get_seasons(session: Session = Depends(get_session)) -> SeasonResponse:
    seasons = list_seasons(session)
    return SeasonResponse(seasons=seasons)


@router.get("/teams", response_model=TeamResponse)
def get_teams(season: int, session: Session = Depends(get_session)) -> TeamResponse:
    teams = list_teams(session, season=season)
    return TeamResponse(season=season, teams=teams)

