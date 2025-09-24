from __future__ import annotations

from datetime import date

from backend.etl.etl_compute_states import CoachWindow, _resolve_playcaller


def test_resolve_playcaller_prefers_explicit_playcaller():
    lookup = {
        "KC": {
            "OC": [
                CoachWindow(
                    coach_id="oc",
                    coach_name="OC",
                    team="KC",
                    role="OC",
                    start_date=date(2024, 1, 1),
                    end_date=None,
                    start_game_id=None,
                    end_game_id=None,
                )
            ],
            "OffPlayCaller": [
                CoachWindow(
                    coach_id="pc",
                    coach_name="PlayCaller",
                    team="KC",
                    role="OffPlayCaller",
                    start_date=date(2024, 9, 1),
                    end_date=None,
                    start_game_id=None,
                    end_game_id=None,
                )
            ],
        }
    }

    result = _resolve_playcaller(lookup, team="KC", side="offense", game_date=date(2024, 9, 10))
    assert result.coach_id == "pc"
    assert result.role == "OffPlayCaller"

