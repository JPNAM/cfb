from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import LineupScoreRequest, LineupScoreResponse
from ..services.metrics import compute_lineup_score

router = APIRouter(prefix="/api/score", tags=["score"])


@router.post("/lineup", response_model=LineupScoreResponse)
def score_lineup(payload: LineupScoreRequest, session: Session = Depends(get_session)) -> LineupScoreResponse:
    try:
        return compute_lineup_score(
            session,
            team=payload.team,
            side=payload.side,
            system_state_id=payload.system_state_id,
            lineup=payload.lineup,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

