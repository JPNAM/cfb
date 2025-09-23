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


@pytest.fixture()
def seed_data(db_session):
    db_session.query(RolePairWeight).delete()
    for side, role_a, role_b, weight in ROLE_WEIGHTS:
        db_session.add(RolePairWeight(side=side, role_a=role_a, role_b=role_b, weight=weight))
        if role_a != role_b:
            db_session.add(RolePairWeight(side=side, role_a=role_b, role_b=role_a, weight=weight))

    db_session.add(Game(game_id="G2", season=2024, week=1, game_date=date(2024, 9, 8), home_team="KC", away_team="LV"))
    db_session.add(SystemState(system_state_id="state-off", team="KC", side="offense", coach_id="c1", coach_name="Coach"))
    db_session.add(SystemState(system_state_id="state-def", team="LV", side="defense", coach_id="c2", coach_name="Coach2"))

    for idx in range(50):
        play_id = f"G2-{idx}"
        db_session.add(
            Play(
                play_id=play_id,
                game_id="G2",
                drive_id=str(idx // 10),
                quarter=1,
                clock_seconds=600 - idx,
                offense_team="KC",
                defense_team="LV",
                play_type="run",
                special_teams=False,
            )
        )
        db_session.add(
            PlaySystemState(
                play_id=play_id,
                offense_system_state_id="state-off",
                defense_system_state_id="state-def",
            )
        )

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

    for gsis_id, role in roles.items():
        db_session.add(Player(gsis_id=gsis_id, display_name=gsis_id, position=role))
        db_session.add(
            PlayerSnapsInState(
                system_state_id="state-off",
                team="KC",
                side="offense",
                gsis_id=gsis_id,
                snaps=40,
            )
        )
        db_session.add(
            PlayerRoleCountInState(
                system_state_id="state-off",
                team="KC",
                side="offense",
                gsis_id=gsis_id,
                role=role,
                snaps=40,
            )
        )

    players = sorted(lineup)
    for i, a in enumerate(players):
        for b in players[i + 1 :]:
            db_session.add(
                CoSnaps(
                    system_state_id="state-off",
                    team="KC",
                    side="offense",
                    a_gsis=a,
                    b_gsis=b,
                    co_snaps=30,
                )
            )

    db_session.flush()
    return lineup


def test_score_endpoint(client, seed_data):
    payload = {
        "team": "KC",
        "side": "offense",
        "system_state_id": "state-off",
        "lineup": seed_data,
    }
    response = client.post("/api/score/lineup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "LSU" in data
    assert data["warnings"] == []


def test_score_endpoint_validates_unique(client, seed_data):
    payload = {
        "team": "KC",
        "side": "offense",
        "system_state_id": "state-off",
        "lineup": seed_data[:10] + [seed_data[0]],
    }
    response = client.post("/api/score/lineup", json=payload)
    assert response.status_code == 422

