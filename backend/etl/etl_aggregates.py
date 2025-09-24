from __future__ import annotations

import itertools
from collections import defaultdict
from typing import Dict, List, Tuple

import typer
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    CoSnaps,
    Play,
    PlayParticipation,
    PlaySystemState,
    PlayerRoleCountInState,
    PlayerSnapsInState,
)
from .util_id_maps import position_to_group

app = typer.Typer(help="Compute snap and co-snap aggregates for each system state")


@app.command()
def main() -> None:
    with SessionLocal() as session:
        rows = session.execute(
            select(
                PlayParticipation.play_id,
                PlayParticipation.side,
                PlayParticipation.gsis_id,
                PlayParticipation.position,
                Play.offense_team,
                Play.defense_team,
                Play.special_teams,
                PlaySystemState.offense_system_state_id,
                PlaySystemState.defense_system_state_id,
            )
            .join(Play, Play.play_id == PlayParticipation.play_id)
            .join(PlaySystemState, PlaySystemState.play_id == Play.play_id)
            .where(PlayParticipation.gsis_id.is_not(None))
        ).all()

        player_snaps: Dict[Tuple[str, str, str, str], int] = defaultdict(int)
        player_roles: Dict[Tuple[str, str, str, str, str], int] = defaultdict(int)
        play_lineups: Dict[Tuple[str, str, str, str], List[str]] = defaultdict(list)

        for row in rows:
            if row.special_teams:
                continue
            side = row.side
            if side == "offense":
                system_state_id = row.offense_system_state_id
                team = row.offense_team
            else:
                system_state_id = row.defense_system_state_id
                team = row.defense_team
            if not system_state_id or not team:
                continue
            key = (system_state_id, team, side, row.gsis_id)
            player_snaps[key] += 1
            role = position_to_group(row.position, side)
            if role:
                player_roles[(system_state_id, team, side, row.gsis_id, role)] += 1
            play_key = (system_state_id, team, side, row.play_id)
            play_lineups[play_key].append(row.gsis_id)

        # compute co-snaps
        co_counts: Dict[Tuple[str, str, str, str, str], int] = defaultdict(int)
        for (system_state_id, team, side, play_id), players in play_lineups.items():
            unique_players = sorted(set(players))
            for a, b in itertools.combinations(unique_players, 2):
                key = (system_state_id, team, side, a, b)
                co_counts[key] += 1

        session.execute(delete(PlayerSnapsInState))
        session.execute(delete(PlayerRoleCountInState))
        session.execute(delete(CoSnaps))

        if player_snaps:
            session.execute(
                PlayerSnapsInState.__table__.insert(),
                [
                    {
                        "system_state_id": k[0],
                        "team": k[1],
                        "side": k[2],
                        "gsis_id": k[3],
                        "snaps": v,
                    }
                    for k, v in player_snaps.items()
                ],
            )

        if player_roles:
            session.execute(
                PlayerRoleCountInState.__table__.insert(),
                [
                    {
                        "system_state_id": k[0],
                        "team": k[1],
                        "side": k[2],
                        "gsis_id": k[3],
                        "role": k[4],
                        "snaps": v,
                    }
                    for k, v in player_roles.items()
                ],
            )

        if co_counts:
            session.execute(
                CoSnaps.__table__.insert(),
                [
                    {
                        "system_state_id": k[0],
                        "team": k[1],
                        "side": k[2],
                        "a_gsis": k[3],
                        "b_gsis": k[4],
                        "co_snaps": v,
                    }
                    for k, v in co_counts.items()
                ],
            )

        session.commit()

    typer.secho("Aggregates recomputed", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()

