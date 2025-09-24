from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import SystemStateLabel, SystemStateSummary
from ..services.system_state_service import list_system_states, system_state_summary

router = APIRouter(prefix="/api/system_state", tags=["system-states"])


@router.get("", response_model=list[SystemStateLabel])
def get_system_states(
    team: str = Query(..., description="Team abbreviation"),
    side: str = Query(..., pattern="^(offense|defense)$"),
    session: Session = Depends(get_session),
) -> list[SystemStateLabel]:
    return list_system_states(session, team=team, side=side)


@router.get("/summary", response_model=SystemStateSummary)
def get_system_state_summary(
    team: str,
    side: str,
    system_state_id: str,
    session: Session = Depends(get_session),
) -> SystemStateSummary:
    states = list_system_states(session, team=team, side=side)
    if not any(state.system_state_id == system_state_id for state in states):
        raise HTTPException(status_code=404, detail="System state not found")
    return system_state_summary(session, team=team, side=side, system_state_id=system_state_id)

