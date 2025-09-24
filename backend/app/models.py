from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Column, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

from .db_types import JSONB

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    game_id = Column(String, primary_key=True)
    season = Column(Integer, nullable=False)
    week = Column(Integer)
    game_date = Column(Date)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)


class Play(Base):
    __tablename__ = "plays"

    play_id = Column(String, primary_key=True)
    game_id = Column(String, ForeignKey("games.game_id"))
    drive_id = Column(String)
    quarter = Column(Integer)
    clock_seconds = Column(Integer)
    offense_team = Column(String)
    defense_team = Column(String)
    play_type = Column(String)
    special_teams = Column(Boolean, default=False)


class PlayParticipation(Base):
    __tablename__ = "play_participation"
    __table_args__ = (
        CheckConstraint("side IN ('offense','defense')"),
    )

    play_id = Column(String, ForeignKey("plays.play_id", ondelete="CASCADE"), primary_key=True)
    side = Column(String, primary_key=True)
    gsis_id = Column(String, primary_key=True)
    position = Column(String)
    jersey_number = Column(Integer)


class Player(Base):
    __tablename__ = "players"

    gsis_id = Column(String, primary_key=True)
    display_name = Column(String)
    position = Column(String)
    team_history = Column(JSONB, default=list)


class CoachRole(Base):
    __tablename__ = "coach_roles"

    coach_id = Column(String, primary_key=True)
    coach_name = Column(String, nullable=False)
    team = Column(String, nullable=False)
    role = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    start_game_id = Column(String)
    end_game_id = Column(String)

    __table_args__ = (
        UniqueConstraint("coach_id", "team", "role", "start_date", name="uq_coach_role_window"),
    )


class SystemState(Base):
    __tablename__ = "system_states"

    system_state_id = Column(String, primary_key=True)
    team = Column(String, nullable=False)
    side = Column(String, nullable=False)
    coach_id = Column(String, nullable=False)
    coach_name = Column(String)
    role = Column(String)
    window_start = Column(Date)
    window_end = Column(Date)
    start_game_id = Column(String)
    end_game_id = Column(String)


class PlaySystemState(Base):
    __tablename__ = "play_system_state"

    play_id = Column(String, ForeignKey("plays.play_id", ondelete="CASCADE"), primary_key=True)
    offense_system_state_id = Column(String)
    defense_system_state_id = Column(String)


class PlayerSnapsInState(Base):
    __tablename__ = "player_snaps_in_state"

    system_state_id = Column(String, primary_key=True)
    team = Column(String, primary_key=True)
    side = Column(String, primary_key=True)
    gsis_id = Column(String, primary_key=True)
    snaps = Column(Integer)


class CoSnaps(Base):
    __tablename__ = "co_snaps"

    system_state_id = Column(String, primary_key=True)
    team = Column(String, primary_key=True)
    side = Column(String, primary_key=True)
    a_gsis = Column(String, primary_key=True)
    b_gsis = Column(String, primary_key=True)
    co_snaps = Column(Integer)


class PlayerRoleCountInState(Base):
    __tablename__ = "player_role_counts_in_state"

    system_state_id = Column(String, primary_key=True)
    team = Column(String, primary_key=True)
    side = Column(String, primary_key=True)
    gsis_id = Column(String, primary_key=True)
    role = Column(String, primary_key=True)
    snaps = Column(Integer)


class RolePairWeight(Base):
    __tablename__ = "role_pair_weights"

    side = Column(String, primary_key=True)
    role_a = Column(String, primary_key=True)
    role_b = Column(String, primary_key=True)
    weight = Column(Numeric)

