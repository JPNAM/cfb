from __future__ import annotations

import hashlib
from datetime import date
from typing import Optional

POSITION_GROUPS_OFFENSE = {
    "QB": "QB",
    "RB": "RB",
    "FB": "RB",
    "HB": "RB",
    "TB": "RB",
    "WR": "WR",
    "TE": "TE",
    "OL": "OL",
    "LT": "OL",
    "RT": "OL",
    "LG": "OL",
    "RG": "OL",
    "C": "OL",
    "G": "OL",
    "OT": "OL",
}

POSITION_GROUPS_DEFENSE = {
    "DL": "DL",
    "DT": "DL",
    "NT": "DL",
    "DE": "DL",
    "EDGE": "DL",
    "LB": "LB",
    "ILB": "LB",
    "OLB": "LB",
    "MLB": "LB",
    "CB": "CB",
    "DB": "CB",
    "S": "S",
    "SS": "S",
    "FS": "S",
}


def position_to_group(position: Optional[str], side: str) -> Optional[str]:
    if not position:
        return None
    position = position.upper()
    if side == "offense":
        return POSITION_GROUPS_OFFENSE.get(position, position)
    return POSITION_GROUPS_DEFENSE.get(position, position)


def hash_system_state(
    *,
    team: str,
    side: str,
    coach_id: str,
    window_start: Optional[date],
    window_end: Optional[date],
    start_game_id: Optional[str],
    end_game_id: Optional[str],
) -> str:
    payload = "|".join(
        [
            team,
            side,
            coach_id or "",
            (window_start.isoformat() if window_start else ""),
            (window_end.isoformat() if window_end else ""),
            start_game_id or "",
            end_game_id or "",
        ]
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def is_offensive_role(role: str) -> bool:
    return role in {"OC", "OffPlayCaller"}


def is_defensive_role(role: str) -> bool:
    return role in {"DC", "DefPlayCaller"}


def normalize_side(side: str) -> str:
    if side not in {"offense", "defense"}:
        raise ValueError(f"Unknown side: {side}")
    return side

