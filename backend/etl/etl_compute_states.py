from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, Optional

import typer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import CoachRole, Game, Play, PlaySystemState, SystemState
from .util_id_maps import hash_system_state

app = typer.Typer(help="Compute system state identifiers per play based on coach windows")


@dataclass
class CoachWindow:
    coach_id: str
    coach_name: str
    team: str
    role: str
    start_date: date
    end_date: Optional[date]
    start_game_id: Optional[str]
    end_game_id: Optional[str]

    def active_on(self, when: date) -> bool:
        if self.start_date and when < self.start_date:
            return False
        if self.end_date and when > self.end_date:
            return False
        return True


ROLE_PRIORITY = {
    "offense": ["OffPlayCaller", "OC"],
    "defense": ["DefPlayCaller", "DC"],
}


def _load_coach_windows(session: Session) -> Dict[str, Dict[str, list[CoachWindow]]]:
    rows = session.execute(select(CoachRole)).scalars().all()
    by_team: Dict[str, Dict[str, list[CoachWindow]]] = {}
    for row in rows:
        window = CoachWindow(
            coach_id=row.coach_id,
            coach_name=row.coach_name,
            team=row.team,
            role=row.role,
            start_date=row.start_date,
            end_date=row.end_date,
            start_game_id=row.start_game_id,
            end_game_id=row.end_game_id,
        )
        by_team.setdefault(row.team, {}).setdefault(row.role, []).append(window)
    for team_roles in by_team.values():
        for role_windows in team_roles.values():
            role_windows.sort(key=lambda w: w.start_date)
    return by_team


def _select_window(windows: Iterable[CoachWindow], when: date) -> Optional[CoachWindow]:
    candidates = [w for w in windows if w.active_on(when)]
    if not candidates:
        return None
    # prefer the most recent start date
    candidates.sort(key=lambda w: w.start_date, reverse=True)
    return candidates[0]


def _resolve_playcaller(
    coach_lookup: Dict[str, Dict[str, list[CoachWindow]]],
    *,
    team: str,
    side: str,
    game_date: date,
) -> CoachWindow:
    priorities = ROLE_PRIORITY[side]
    team_roles = coach_lookup.get(team, {})
    for role in priorities:
        windows = team_roles.get(role, [])
        match = _select_window(windows, game_date)
        if match:
            return match
    raise RuntimeError(f"No coach role found for {team} {side} on {game_date}")


@app.command()
def main() -> None:
    with SessionLocal() as session:
        coach_lookup = _load_coach_windows(session)
        plays = (
            session.execute(
                select(
                    Play.play_id,
                    Play.game_id,
                    Play.offense_team,
                    Play.defense_team,
                    Game.game_date,
                ).join(Game, Game.game_id == Play.game_id)
            )
            .all()
        )

        state_cache: Dict[str, SystemState] = {}

        for play in plays:
            game_date = play.game_date
            offense_team = play.offense_team
            defense_team = play.defense_team

            if offense_team is None or defense_team is None or game_date is None:
                continue

            off_window = _resolve_playcaller(coach_lookup, team=offense_team, side="offense", game_date=game_date)
            def_window = _resolve_playcaller(coach_lookup, team=defense_team, side="defense", game_date=game_date)

            off_state_id = hash_system_state(
                team=offense_team,
                side="offense",
                coach_id=off_window.coach_id,
                window_start=off_window.start_date,
                window_end=off_window.end_date,
                start_game_id=off_window.start_game_id,
                end_game_id=off_window.end_game_id,
            )
            def_state_id = hash_system_state(
                team=defense_team,
                side="defense",
                coach_id=def_window.coach_id,
                window_start=def_window.start_date,
                window_end=def_window.end_date,
                start_game_id=def_window.start_game_id,
                end_game_id=def_window.end_game_id,
            )

            if off_state_id not in state_cache:
                state_cache[off_state_id] = SystemState(
                    system_state_id=off_state_id,
                    team=offense_team,
                    side="offense",
                    coach_id=off_window.coach_id,
                    coach_name=off_window.coach_name,
                    role=off_window.role,
                    window_start=off_window.start_date,
                    window_end=off_window.end_date,
                    start_game_id=off_window.start_game_id,
                    end_game_id=off_window.end_game_id,
                )
            if def_state_id not in state_cache:
                state_cache[def_state_id] = SystemState(
                    system_state_id=def_state_id,
                    team=defense_team,
                    side="defense",
                    coach_id=def_window.coach_id,
                    coach_name=def_window.coach_name,
                    role=def_window.role,
                    window_start=def_window.start_date,
                    window_end=def_window.end_date,
                    start_game_id=def_window.start_game_id,
                    end_game_id=def_window.end_game_id,
                )

            session.merge(
                PlaySystemState(
                    play_id=play.play_id,
                    offense_system_state_id=off_state_id,
                    defense_system_state_id=def_state_id,
                )
            )

        for state in state_cache.values():
            session.merge(state)

        session.commit()

    typer.secho("Computed system states for plays", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()

