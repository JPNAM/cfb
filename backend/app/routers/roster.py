from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import RosterPlayer
from ..services.roster import get_roster

router = APIRouter(prefix="/api", tags=["roster"])


@router.get("/roster", response_model=list[RosterPlayer])
def roster(
    team: str = Query(..., description="Team abbreviation"),
    side: str = Query(..., pattern="^(offense|defense)$"),
    system_state_id: str | None = Query(None, description="Optional system state"),
    session: Session = Depends(get_session),
) -> list[RosterPlayer]:
    return get_roster(session, team=team, side=side, system_state_id=system_state_id)

