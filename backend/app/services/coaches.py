from __future__ import annotations

from datetime import date
from typing import Dict, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..models import CoachRole
from ..schemas import CoachRoleResponse, CoachesActiveResponse

ROLE_LOOKUP = {
    "offense_playcaller": "OffPlayCaller",
    "defense_playcaller": "DefPlayCaller",
    "oc": "OC",
    "dc": "DC",
}


def _role_to_response(row: CoachRole | None) -> Optional[CoachRoleResponse]:
    if row is None:
        return None
    return CoachRoleResponse(
        coach_id=row.coach_id,
        coach_name=row.coach_name,
        team=row.team,
        role=row.role,
        start_date=row.start_date,
        end_date=row.end_date,
        start_game_id=row.start_game_id,
        end_game_id=row.end_game_id,
    )


def _active_role(session: Session, *, team: str, role: str, on_date: date) -> CoachRole | None:
    query = (
        select(CoachRole)
        .where(CoachRole.team == team)
        .where(CoachRole.role == role)
        .where(CoachRole.start_date <= on_date)
        .where(or_(CoachRole.end_date.is_(None), CoachRole.end_date >= on_date))
        .order_by(CoachRole.start_date.desc())
    )
    return session.execute(query).scalars().first()


def active_coaches(session: Session, *, team: str, on_date: date) -> CoachesActiveResponse:
    offense = _active_role(session, team=team, role=ROLE_LOOKUP["offense_playcaller"], on_date=on_date)
    defense = _active_role(session, team=team, role=ROLE_LOOKUP["defense_playcaller"], on_date=on_date)
    oc = _active_role(session, team=team, role=ROLE_LOOKUP["oc"], on_date=on_date)
    dc = _active_role(session, team=team, role=ROLE_LOOKUP["dc"], on_date=on_date)

    # fallback if explicit play caller missing
    if offense is None:
        offense = oc
    if defense is None:
        defense = dc

    return CoachesActiveResponse(
        offense_playcaller=_role_to_response(offense),
        defense_playcaller=_role_to_response(defense),
        oc=_role_to_response(oc),
        dc=_role_to_response(dc),
    )

