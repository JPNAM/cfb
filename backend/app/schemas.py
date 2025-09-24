from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class SeasonResponse(BaseModel):
    seasons: List[int]


class TeamResponse(BaseModel):
    season: int
    teams: List[str]


class SystemStateLabel(BaseModel):
    system_state_id: str
    team: str
    side: str
    coach_id: str
    coach_name: Optional[str]
    role: Optional[str]
    window_start: Optional[date]
    window_end: Optional[date]
    start_game_id: Optional[str]
    end_game_id: Optional[str]
    total_snaps: Optional[int] = 0

    @property
    def label(self) -> str:
        role = self.role or "Play Caller"
        name = self.coach_name or "Unknown"
        if self.window_start and self.window_end:
            return f"{name} ({role}) — {self.window_start} to {self.window_end}"
        if self.window_start:
            return f"{name} ({role}) — from {self.window_start}"
        return f"{name} ({role})"


class RosterPlayer(BaseModel):
    gsis_id: str
    name: str
    position: Optional[str]
    position_group: Optional[str]
    snaps_in_state: int = 0
    ius: float = 0.0
    roles_breakdown: Dict[str, int] = Field(default_factory=dict)
    n_system_states_seen: int = 0


class LineupScoreRequest(BaseModel):
    team: str
    side: str
    system_state_id: str
    lineup: List[str]

    @field_validator("lineup")
    @classmethod
    def validate_lineup(cls, value: List[str]) -> List[str]:
        if len(value) != 11:
            raise ValueError("Lineup must contain exactly 11 GSIS IDs")
        if len(set(value)) != 11:
            raise ValueError("Lineup must contain 11 unique GSIS IDs")
        return value


class PlayerScore(BaseModel):
    gsis_id: str
    snaps_in_state: int
    ius: float
    roles: Dict[str, int]


class PairEdge(BaseModel):
    a: str
    b: str
    weight: float
    jaccard: float
    co_snaps: int
    n_i: int
    n_j: int


class LineupScoreResponse(BaseModel):
    LSU: float
    LIU: float
    LIC: float
    cohesion: float
    warnings: List[str] = Field(default_factory=list)
    per_player: List[PlayerScore]
    pair_edges: List[PairEdge]
    playcaller_label: Optional[str] = None


class CoachRoleResponse(BaseModel):
    coach_id: str
    coach_name: str
    team: str
    role: str
    start_date: Optional[date]
    end_date: Optional[date]
    start_game_id: Optional[str]
    end_game_id: Optional[str]


class CoachesActiveResponse(BaseModel):
    offense_playcaller: Optional[CoachRoleResponse]
    defense_playcaller: Optional[CoachRoleResponse]
    oc: Optional[CoachRoleResponse]
    dc: Optional[CoachRoleResponse]


class SystemStateSummary(BaseModel):
    system_state_id: str
    team_snaps: int
    distinct_players: int
    top_pairs: List[PairEdge]
    position_mix: Dict[str, int]

