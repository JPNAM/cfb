from __future__ import annotations

import itertools
import math
from decimal import Decimal
from typing import Dict, Iterable, List, Sequence, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from ..models import (
    CoSnaps,
    Play,
    PlaySystemState,
    Player,
    PlayerRoleCountInState,
    PlayerSnapsInState,
    RolePairWeight,
    SystemState,
)
from ..schemas import LineupScoreResponse, PairEdge, PlayerScore


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _safe_float(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _team_snaps(session: Session, *, team: str, side: str, system_state_id: str) -> int:
    condition = (
        PlaySystemState.offense_system_state_id == system_state_id
        if side == "offense"
        else PlaySystemState.defense_system_state_id == system_state_id
    )
    team_condition = Play.offense_team == team if side == "offense" else Play.defense_team == team

    value = (
        session.execute(
            select(func.count())
            .select_from(Play)
            .join(PlaySystemState, PlaySystemState.play_id == Play.play_id)
            .where(condition)
            .where(team_condition)
            .where(Play.special_teams.is_(False))
        ).scalar()
        or 0
    )
    return int(value)


def compute_lineup_score(
    session: Session,
    *,
    team: str,
    side: str,
    system_state_id: str,
    lineup: Sequence[str],
) -> LineupScoreResponse:
    lineup = list(dict.fromkeys(lineup))
    if len(lineup) != 11:
        raise ValueError("Lineup must contain exactly 11 unique players")

    team_snaps = _team_snaps(session, team=team, side=side, system_state_id=system_state_id)

    snaps_rows = session.execute(
        select(PlayerSnapsInState.gsis_id, PlayerSnapsInState.snaps)
        .where(
            and_(
                PlayerSnapsInState.system_state_id == system_state_id,
                PlayerSnapsInState.team == team,
                PlayerSnapsInState.side == side,
                PlayerSnapsInState.gsis_id.in_(lineup),
            )
        )
    ).all()
    snaps_map: Dict[str, int] = {row.gsis_id: row.snaps for row in snaps_rows}
    snaps_values = [snaps_map.get(pid, 0) for pid in lineup]

    lsu_values = [snaps / team_snaps for snaps in snaps_values] if team_snaps else [0.0] * len(lineup)
    LSU = _mean(lsu_values)

    role_rows = session.execute(
        select(
            PlayerRoleCountInState.gsis_id,
            PlayerRoleCountInState.role,
            PlayerRoleCountInState.snaps,
        ).where(
            and_(
                PlayerRoleCountInState.system_state_id == system_state_id,
                PlayerRoleCountInState.team == team,
                PlayerRoleCountInState.side == side,
                PlayerRoleCountInState.gsis_id.in_(lineup),
            )
        )
    ).all()

    roles_map: Dict[str, Dict[str, int]] = {}
    for row in role_rows:
        roles_map.setdefault(row.gsis_id, {})[row.role] = row.snaps

    player_scores: List[PlayerScore] = []
    ius_values: List[float] = []
    dominant_roles: Dict[str, str | None] = {}
    for player_id in lineup:
        counts = roles_map.get(player_id, {})
        total_snaps = sum(counts.values())
        if total_snaps == 0:
            ius = 0.0
        elif len(counts) == 1:
            ius = 1.0
        else:
            entropy = 0.0
            for snaps in counts.values():
                prob = snaps / total_snaps
                if prob > 0:
                    entropy -= prob * math.log(prob)
            max_entropy = math.log(len(counts)) if len(counts) > 1 else 1.0
            ius = 1.0 - (entropy / max_entropy if max_entropy else 0.0)
        dominant_roles[player_id] = max(counts.items(), key=lambda kv: kv[1])[0] if counts else None
        ius_values.append(ius)
        player_scores.append(
            PlayerScore(
                gsis_id=player_id,
                snaps_in_state=snaps_map.get(player_id, 0),
                ius=ius,
                roles=counts,
            )
        )

    LIU = _mean(ius_values)

    pair_weights_rows = session.execute(
        select(RolePairWeight.role_a, RolePairWeight.role_b, RolePairWeight.weight)
        .where(RolePairWeight.side == side)
    ).all()
    pair_weights: Dict[Tuple[str, str], float] = {}
    for row in pair_weights_rows:
        pair_weights[(row.role_a, row.role_b)] = _safe_float(row.weight)

    positions_rows = session.execute(
        select(Player.gsis_id, Player.position).where(Player.gsis_id.in_(lineup))
    ).all()
    position_map: Dict[str, str | None] = {row.gsis_id: row.position for row in positions_rows}

    co_rows = session.execute(
        select(CoSnaps.a_gsis, CoSnaps.b_gsis, CoSnaps.co_snaps)
        .where(
            and_(
                CoSnaps.system_state_id == system_state_id,
                CoSnaps.team == team,
                CoSnaps.side == side,
                CoSnaps.a_gsis.in_(lineup),
                CoSnaps.b_gsis.in_(lineup),
            )
        )
    ).all()
    co_map: Dict[Tuple[str, str], int] = {}
    for row in co_rows:
        key = tuple(sorted((row.a_gsis, row.b_gsis)))
        co_map[key] = row.co_snaps

    pair_edges: List[PairEdge] = []
    weight_total = 0.0
    weighted_sum = 0.0

    for a, b in itertools.combinations(lineup, 2):
        role_a = dominant_roles.get(a) or position_map.get(a)
        role_b = dominant_roles.get(b) or position_map.get(b)
        if not role_a or not role_b:
            continue
        weight = pair_weights.get((role_a, role_b)) or pair_weights.get((role_b, role_a))
        if weight is None:
            continue

        n_i = snaps_map.get(a, 0)
        n_j = snaps_map.get(b, 0)
        co_snaps = co_map.get(tuple(sorted((a, b))), 0)
        denom = n_i + n_j - co_snaps
        jaccard = (co_snaps / denom) if denom > 0 else 0.0

        weighted_sum += weight * jaccard
        weight_total += weight
        pair_edges.append(
            PairEdge(
                a=a,
                b=b,
                weight=weight,
                jaccard=jaccard,
                co_snaps=co_snaps,
                n_i=n_i,
                n_j=n_j,
            )
        )

    LIC = weighted_sum / weight_total if weight_total else 0.0

    cohesion = 0.35 * LSU + 0.20 * LIU + 0.45 * LIC

    state = session.get(SystemState, system_state_id)
    playcaller_label = None
    if state:
        role = state.role or "Play Caller"
        window = ""
        if state.window_start and state.window_end:
            window = f" — {state.window_start} to {state.window_end}"
        elif state.window_start:
            window = f" — from {state.window_start}"
        playcaller_label = f"{state.coach_name or state.coach_id} ({role}){window}"

    warnings: List[str] = []
    for player_id, snaps in zip(lineup, snaps_values):
        if snaps == 0:
            warnings.append(f"Player {player_id} has zero snaps in this system state")

    return LineupScoreResponse(
        LSU=LSU,
        LIU=LIU,
        LIC=LIC,
        cohesion=cohesion,
        warnings=warnings,
        per_player=player_scores,
        pair_edges=pair_edges,
        playcaller_label=playcaller_label,
    )

