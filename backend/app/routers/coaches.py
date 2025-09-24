from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import CoachesActiveResponse
from ..services.coaches import active_coaches

router = APIRouter(prefix="/api/coaches", tags=["coaches"])


@router.get("/active", response_model=CoachesActiveResponse)
def get_active_coaches(
    team: str = Query(..., description="Team abbreviation"),
    date_param: date = Query(default=date.today(), alias="date"),
    session: Session = Depends(get_session),
) -> CoachesActiveResponse:
    return active_coaches(session, team=team, on_date=date_param)

