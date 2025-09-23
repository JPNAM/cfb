from __future__ import annotations

from datetime import date

import pytest

from app.models import (
    CoSnaps,
    Game,
    Play,
    PlaySystemState,
    Player,
    PlayerRoleCountInState,
    PlayerSnapsInState,
    RolePairWeight,
    SystemState,
)
from app.services.metrics import compute_lineup_score

ROLE_WEIGHTS = [
    ("offense", "OL", "OL", 1.0),
    ("offense", "QB", "OL", 0.8),
    ("offense", "QB", "WR", 0.85),
    ("offense", "QB", "TE", 0.8),
    ("offense", "QB", "RB", 0.7),
    ("offense", "WR", "WR", 0.4),
    ("offense", "WR", "TE", 0.5),
    ("offense", "RB", "OL", 0.7),
    ("offense", "RB", "TE", 0.55),
    ("offense", "RB", "WR", 0.4),
    ("offense", "TE", "OL", 0.7),
]


@pytest.fixture(autouse=True)
def seed_role_weights(db_session):
    db_session.query(RolePairWeight).delete()
    for side, role_a, role_b, weight in ROLE_WEIGHTS:
        db_session.add(RolePairWeight(side=side, role_a=role_a, role_b=role_b, weight=weight))
        if role_a != role_b:
            db_session.add(RolePairWeight(side=side, role_a=role_b, role_b=role_a, weight=weight))
    db_session.flush()


def test_compute_metrics_happy_path(db_session):
    lineup = [
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6",
        "P7",
        "P8",
        "P9",
        "P10",
        "P11",
    ]
    roles = {
        "P1": "QB",
        "P2": "RB",
        "P3": "WR",
        "P4": "WR",
        "P5": "WR",
        "P6": "TE",
        "P7": "OL",
        "P8": "OL",
        "P9": "OL",
        "P10": "OL",
        "P11": "OL",
    }

    offense_state_id = "state-off"
    defense_state_id = "state-def"

    db_session.add(Game(game_id="G1", season=2024, week=1, game_date=date(2024, 9, 8), home_team="KC", away_team="LV"))
    db_session.add(SystemState(system_state_id=offense_state_id, team="KC", side="offense", coach_id="c1"))
    db_session.add(SystemState(system_state_id=defense_state_id, team="LV", side="defense", coach_id="c2"))

    for idx in range(100):
        play_id = f"G1-{idx}"
        db_session.add(
            Play(
                play_id=play_id,
                game_id="G1",
                drive_id=str(idx // 10),
                quarter=1,
                clock_seconds=600 - idx,
                offense_team="KC",
                defense_team="LV",
                play_type="pass",
                special_teams=False,
            )
        )
        db_session.add(
            PlaySystemState(
                play_id=play_id,
                offense_system_state_id=offense_state_id,
                defense_system_state_id=defense_state_id,
            )
        )

    for gsis_id, role in roles.items():
        db_session.add(Player(gsis_id=gsis_id, display_name=gsis_id, position=role))
        db_session.add(
            PlayerSnapsInState(
                system_state_id=offense_state_id,
                team="KC",
                side="offense",
                gsis_id=gsis_id,
                snaps=90,
            )
        )
        db_session.add(
            PlayerRoleCountInState(
                system_state_id=offense_state_id,
                team="KC",
                side="offense",
                gsis_id=gsis_id,
                role=role,
                snaps=90,
            )
        )

    players = sorted(lineup)
    for i, a in enumerate(players):
        for b in players[i + 1 :]:
            db_session.add(
                CoSnaps(
                    system_state_id=offense_state_id,
                    team="KC",
                    side="offense",
                    a_gsis=a,
                    b_gsis=b,
                    co_snaps=80,
                )
            )

    db_session.commit()

    score = compute_lineup_score(
        db_session,
        team="KC",
        side="offense",
        system_state_id=offense_state_id,
        lineup=lineup,
    )

    assert score.LSU == pytest.approx(0.9, rel=1e-3)
    assert score.LIU == pytest.approx(1.0, rel=1e-6)
    assert score.LIC == pytest.approx(0.8, rel=1e-3)
    expected = 0.35 * 0.9 + 0.20 * 1.0 + 0.45 * 0.8
    assert score.cohesion == pytest.approx(expected, rel=1e-3)

