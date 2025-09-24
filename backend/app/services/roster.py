from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from ..models import Player, PlayerRoleCountInState, PlayerSnapsInState
from ..schemas import RosterPlayer

POSITION_GROUP_MAP = {
    "QB": "QB",
    "RB": "RB",
    "FB": "RB",
    "HB": "RB",
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
    "DT": "DL",
    "NT": "DL",
    "DE": "DL",
    "EDGE": "DL",
    "DL": "DL",
    "LB": "LB",
    "ILB": "LB",
    "OLB": "LB",
    "MLB": "LB",
    "CB": "CB",
    "DB": "CB",
    "S": "S",
    "FS": "S",
    "SS": "S",
}


def _position_group(position: Optional[str]) -> Optional[str]:
    if not position:
        return None
    position = position.upper()
    return POSITION_GROUP_MAP.get(position, position)


def _ius_from_counts(counts: Dict[str, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    if len(counts) == 1:
        return 1.0
    import math

    entropy = 0.0
    for snaps in counts.values():
        prob = snaps / total
        if prob > 0:
            entropy -= prob * math.log(prob)
    max_entropy = math.log(len(counts)) if len(counts) > 1 else 1.0
    return 1.0 - (entropy / max_entropy if max_entropy else 0.0)


def get_roster(
    session: Session,
    *,
    team: str,
    side: str,
    system_state_id: Optional[str] = None,
) -> List[RosterPlayer]:
    snaps_query = select(PlayerSnapsInState).where(
        and_(
            PlayerSnapsInState.team == team,
            PlayerSnapsInState.side == side,
        )
    )
    if system_state_id:
        snaps_query = snaps_query.where(PlayerSnapsInState.system_state_id == system_state_id)

    snaps_rows = session.execute(snaps_query).scalars().all()
    player_ids = [row.gsis_id for row in snaps_rows]
    snaps_by_player = {row.gsis_id: row.snaps for row in snaps_rows}

    role_query = select(
        PlayerRoleCountInState.gsis_id,
        PlayerRoleCountInState.role,
        PlayerRoleCountInState.snaps,
    ).where(
        and_(
            PlayerRoleCountInState.team == team,
            PlayerRoleCountInState.side == side,
        )
    )
    if system_state_id:
        role_query = role_query.where(PlayerRoleCountInState.system_state_id == system_state_id)
    role_rows = session.execute(role_query).all()
    roles_map: Dict[str, Dict[str, int]] = defaultdict(dict)
    for row in role_rows:
        roles_map[row.gsis_id][row.role] = row.snaps

    players_map = {}
    if player_ids:
        players_rows = session.execute(
            select(Player.gsis_id, Player.display_name, Player.position)
            .where(Player.gsis_id.in_(player_ids))
        ).all()
        players_map = {row.gsis_id: row for row in players_rows}

    if not player_ids and not system_state_id:
        players_rows = session.execute(
            select(Player.gsis_id, Player.display_name, Player.position)
            .limit(100)
        ).all()
        players_map = {row.gsis_id: row for row in players_rows}

    counts_rows = session.execute(
        select(
            PlayerSnapsInState.gsis_id,
            func.count(func.distinct(PlayerSnapsInState.system_state_id)),
        )
        .where(PlayerSnapsInState.team == team)
        .where(PlayerSnapsInState.side == side)
        .group_by(PlayerSnapsInState.gsis_id)
    ).all()
    counts_map = {row[0]: int(row[1]) for row in counts_rows}

    roster: List[RosterPlayer] = []
    for player_id, player_row in players_map.items():
        roles = roles_map.get(player_id, {})
        position_group = None
        if roles:
            position_group = max(roles.items(), key=lambda kv: kv[1])[0]
        else:
            position_group = _position_group(player_row.position if player_row else None)
        roster.append(
            RosterPlayer(
                gsis_id=player_id,
                name=getattr(player_row, "display_name", player_id),
                position=getattr(player_row, "position", None),
                position_group=position_group,
                snaps_in_state=snaps_by_player.get(player_id, 0),
                ius=_ius_from_counts(roles),
                roles_breakdown=roles,
                n_system_states_seen=counts_map.get(player_id, 0),
            )
        )

    roster.sort(key=lambda r: (-r.snaps_in_state, r.name))
    return roster

