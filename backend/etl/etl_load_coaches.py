from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import CoachRole

app = typer.Typer(help="Load coordinator and play-caller roles from CSV seeds.")


def _parse_date(value: str | None) -> Optional[datetime.date]:
    if value is None or value.strip() == "":
        return None
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


@app.command()
def load(csv_path: Path = typer.Option(Path("seeds/coach_roles.csv"), help="Path to coach roles CSV")) -> None:
    settings = get_settings()
    path = csv_path if csv_path.is_file() else Path.cwd() / csv_path
    if not path.exists():
        raise typer.BadParameter(f"CSV not found: {path}")

    with path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with SessionLocal() as session:  # type: Session
        session.execute(delete(CoachRole))
        for row in rows:
            session.execute(
                insert(CoachRole).values(
                    coach_id=row["coach_id"],
                    coach_name=row.get("coach_name"),
                    team=row.get("team"),
                    role=row.get("role"),
                    start_date=_parse_date(row.get("start_date")),
                    end_date=_parse_date(row.get("end_date")),
                    start_game_id=row.get("start_game_id") or None,
                    end_game_id=row.get("end_game_id") or None,
                )
            )
        session.commit()
    typer.secho(f"Loaded {len(rows)} coach role rows into {settings.database_url}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()

