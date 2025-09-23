from __future__ import annotations

from typing import List

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from ..models import (
    CoSnaps,
    Game,
    Play,
    PlaySystemState,
    PlayerRoleCountInState,
    PlayerSnapsInState,
    SystemState,
)
from ..schemas import PairEdge, SystemStateLabel, SystemStateSummary


def list_seasons(session: Session) -> List[int]:
    rows = session.execute(select(func.distinct(Game.season))).all()
    return sorted(int(row[0]) for row in rows if row[0] is not None)


def list_teams(session: Session, *, season: int | None = None) -> List[str]:
    home_query = select(func.distinct(Game.home_team))
    away_query = select(func.distinct(Game.away_team))
    if season is not None:
        home_query = home_query.where(Game.season == season)
        away_query = away_query.where(Game.season == season)
    home_rows = session.execute(home_query).all()
    away_rows = session.execute(away_query).all()
    teams = {row[0] for row in home_rows if row[0]} | {row[0] for row in away_rows if row[0]}
    return sorted(teams)


def team_snaps(session: Session, *, team: str, side: str, system_state_id: str) -> int:
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


def list_system_states(session: Session, *, team: str, side: str) -> List[SystemStateLabel]:
    rows = (
        session.execute(
            select(SystemState).where(SystemState.team == team).where(SystemState.side == side)
        )
        .scalars()
        .all()
    )
    labels: List[SystemStateLabel] = []
    for state in rows:
        snaps = team_snaps(session, team=team, side=side, system_state_id=state.system_state_id)
        labels.append(
            SystemStateLabel(
                system_state_id=state.system_state_id,
                team=state.team,
                side=state.side,
                coach_id=state.coach_id,
                coach_name=state.coach_name,
                role=state.role,
                window_start=state.window_start,
                window_end=state.window_end,
                start_game_id=state.start_game_id,
                end_game_id=state.end_game_id,
                total_snaps=snaps,
            )
        )
    labels.sort(key=lambda s: ((s.window_start or 0), s.system_state_id))
    return labels


def system_state_summary(
    session: Session,
    *,
    team: str,
    side: str,
    system_state_id: str,
) -> SystemStateSummary:
    snaps = team_snaps(session, team=team, side=side, system_state_id=system_state_id)
    distinct_players = session.execute(
        select(func.count(func.distinct(PlayerSnapsInState.gsis_id)))
        .where(PlayerSnapsInState.system_state_id == system_state_id)
        .where(PlayerSnapsInState.team == team)
        .where(PlayerSnapsInState.side == side)
    ).scalar() or 0

    pair_rows = session.execute(
        select(
            CoSnaps.a_gsis,
            CoSnaps.b_gsis,
            CoSnaps.co_snaps,
            PlayerSnapsInState.snaps.label("n_i"),
        )
        .join(
            PlayerSnapsInState,
            and_(
                PlayerSnapsInState.system_state_id == CoSnaps.system_state_id,
                PlayerSnapsInState.team == CoSnaps.team,
                PlayerSnapsInState.side == CoSnaps.side,
                PlayerSnapsInState.gsis_id == CoSnaps.a_gsis,
            ),
        )
        .where(CoSnaps.system_state_id == system_state_id)
        .where(CoSnaps.team == team)
        .where(CoSnaps.side == side)
        .order_by(CoSnaps.co_snaps.desc())
        .limit(15)
    ).all()

    top_pairs: List[PairEdge] = []
    for row in pair_rows:
        n_i = row.n_i or 0
        n_j = session.execute(
            select(PlayerSnapsInState.snaps)
            .where(PlayerSnapsInState.system_state_id == system_state_id)
            .where(PlayerSnapsInState.team == team)
            .where(PlayerSnapsInState.side == side)
            .where(PlayerSnapsInState.gsis_id == row.b_gsis)
        ).scalar() or 0
        denom = n_i + n_j - row.co_snaps
        jaccard = (row.co_snaps / denom) if denom > 0 else 0.0
        top_pairs.append(
            PairEdge(
                a=row.a_gsis,
                b=row.b_gsis,
                weight=1.0,
                jaccard=jaccard,
                co_snaps=row.co_snaps,
                n_i=n_i,
                n_j=n_j,
            )
        )

    position_rows = session.execute(
        select(PlayerRoleCountInState.role, func.sum(PlayerRoleCountInState.snaps))
        .where(PlayerRoleCountInState.system_state_id == system_state_id)
        .where(PlayerRoleCountInState.team == team)
        .where(PlayerRoleCountInState.side == side)
        .group_by(PlayerRoleCountInState.role)
    ).all()
    position_mix = {row.role: int(row[1]) for row in position_rows}

    return SystemStateSummary(
        system_state_id=system_state_id,
        team_snaps=snaps,
        distinct_players=int(distinct_players),
        top_pairs=top_pairs,
        position_mix=position_mix,
    )

