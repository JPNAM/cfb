from __future__ import annotations

import ast
import math
from datetime import datetime
from typing import Iterable, List, Optional

import pandas as pd
import typer
from nfl_data_py import import_participation_data, import_pbp_data, import_players
from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Game, Play, PlayParticipation, Player

app = typer.Typer(help="Load nflverse games, plays, participation, and players data")


def _ensure_list(value) -> List[dict]:
    if value is None:
        return []
    if isinstance(value, float) and math.isnan(value):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip() == "":
        return []
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return []


def _parse_date(value: str | None) -> Optional[datetime.date]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return datetime.strptime(value, "%Y-%m-%d").date()


def _load_games(session: Session, pbp: pd.DataFrame, force: bool = False) -> None:
    games = pbp[["game_id", "season", "week", "game_date", "home_team", "away_team"]].drop_duplicates("game_id")
    games["game_date"] = games["game_date"].apply(_parse_date)
    games = games.where(pd.notnull(games), None)
    if force:
        session.execute(delete(Game).where(Game.game_id.in_(games["game_id"].tolist())))
    rows = games.to_dict(orient="records")
    for row in rows:
        session.merge(Game(**row))


def _load_players(session: Session, players_df: pd.DataFrame) -> None:
    players_df = players_df.rename(columns={"player_id": "gsis_id"})
    rows = players_df[["gsis_id", "display_name", "position"]].drop_duplicates("gsis_id").to_dict("records")
    for row in rows:
        session.merge(Player(**row))


def _play_id(row: pd.Series) -> str:
    return f"{row['game_id']}-{int(row['play_id'])}"


def _load_plays(session: Session, pbp: pd.DataFrame, force: bool = False) -> List[str]:
    pbp = pbp.copy()
    pbp = pbp[pbp["play_id"].notnull()]
    pbp["play_unique_id"] = pbp.apply(_play_id, axis=1)
    plays_df = pbp[
        [
            "play_unique_id",
            "game_id",
            "drive",
            "qtr",
            "game_seconds_remaining",
            "posteam",
            "defteam",
            "play_type",
            "special_teams_play",
        ]
    ].rename(
        columns={
            "play_unique_id": "play_id",
            "drive": "drive_id",
            "qtr": "quarter",
            "game_seconds_remaining": "clock_seconds",
            "posteam": "offense_team",
            "defteam": "defense_team",
            "special_teams_play": "special_teams",
        }
    )
    plays_df["clock_seconds"] = plays_df["clock_seconds"].fillna(0).astype(int)
    plays_df["special_teams"] = plays_df["special_teams"].fillna(False)
    plays_df = plays_df.where(pd.notnull(plays_df), None)
    if force:
        session.execute(delete(Play).where(Play.play_id.in_(plays_df["play_id"].tolist())))
    rows = plays_df.to_dict("records")
    if rows:
        session.execute(insert(Play), rows)
    return plays_df["play_id"].tolist()


def _load_participation(session: Session, part: pd.DataFrame, play_ids: Iterable[str], force: bool = False) -> None:
    if part.empty:
        return
    part = part.copy()
    part = part[part["play_id"].notnull()]
    part["play_unique_id"] = part.apply(lambda r: f"{r['game_id']}-{int(r['play_id'])}", axis=1)
    part = part[part["play_unique_id"].isin(set(play_ids))]

    if force and not part.empty:
        session.execute(
            delete(PlayParticipation).where(PlayParticipation.play_id.in_(part["play_unique_id"].tolist()))
        )

    payload = []
    for _, row in part.iterrows():
        play_id = row["play_unique_id"]
        for side in ("offense", "defense"):
            players = _ensure_list(row.get(f"{side}_players"))
            for player in players:
                payload.append(
                    {
                        "play_id": play_id,
                        "side": side,
                        "gsis_id": player.get("gsis_id"),
                        "position": player.get("position"),
                        "jersey_number": player.get("jersey_number"),
                    }
                )
    if payload:
        session.execute(insert(PlayParticipation), payload)


@app.command()
def main(
    seasons: List[int] = typer.Option(..., help="List of NFL seasons to load"),
    force: bool = typer.Option(False, help="Delete existing rows for selected seasons"),
) -> None:
    pbp = import_pbp_data(seasons)
    participation = import_participation_data(seasons)
    players_df = import_players()

    with SessionLocal() as session:
        _load_games(session, pbp, force=force)
        play_ids = _load_plays(session, pbp, force=force)
        _load_participation(session, participation, play_ids, force=force)
        _load_players(session, players_df)
        session.commit()

    typer.secho(f"Loaded data for seasons {seasons}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()

