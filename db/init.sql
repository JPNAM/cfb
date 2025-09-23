-- Database initialization for NFL lineup cohesion platform
-- Schema derived from project specification with light extensions for metadata tables.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS games (
  game_id TEXT PRIMARY KEY,
  season INT NOT NULL,
  week INT,
  game_date DATE,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plays (
  play_id TEXT PRIMARY KEY,
  game_id TEXT REFERENCES games(game_id),
  drive_id TEXT,
  quarter INT,
  clock_seconds INT,
  offense_team TEXT,
  defense_team TEXT,
  play_type TEXT,
  special_teams BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_plays_game_id ON plays(game_id);
CREATE INDEX IF NOT EXISTS idx_plays_offense_team ON plays(offense_team);
CREATE INDEX IF NOT EXISTS idx_plays_defense_team ON plays(defense_team);

CREATE TABLE IF NOT EXISTS play_participation (
  play_id TEXT REFERENCES plays(play_id) ON DELETE CASCADE,
  side TEXT CHECK (side IN ('offense','defense')),
  gsis_id TEXT,
  position TEXT,
  jersey_number INT,
  PRIMARY KEY (play_id, side, gsis_id)
);

CREATE INDEX IF NOT EXISTS idx_play_participation_play ON play_participation(play_id);
CREATE INDEX IF NOT EXISTS idx_play_participation_player ON play_participation(gsis_id, side);

CREATE TABLE IF NOT EXISTS players (
  gsis_id TEXT PRIMARY KEY,
  display_name TEXT,
  position TEXT,
  team_history JSONB DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS coach_roles (
  coach_id TEXT,
  coach_name TEXT,
  team TEXT,
  role TEXT,
  start_date DATE,
  end_date DATE,
  start_game_id TEXT NULL,
  end_game_id   TEXT NULL,
  PRIMARY KEY (coach_id, team, role, start_date)
);

CREATE TABLE IF NOT EXISTS system_states (
  system_state_id TEXT PRIMARY KEY,
  team TEXT NOT NULL,
  side TEXT CHECK (side IN ('offense','defense')) NOT NULL,
  coach_id TEXT NOT NULL,
  coach_name TEXT,
  role TEXT,
  window_start DATE,
  window_end DATE,
  start_game_id TEXT,
  end_game_id TEXT
);

CREATE TABLE IF NOT EXISTS play_system_state (
  play_id TEXT PRIMARY KEY REFERENCES plays(play_id) ON DELETE CASCADE,
  offense_system_state_id TEXT,
  defense_system_state_id TEXT
);

CREATE TABLE IF NOT EXISTS player_snaps_in_state (
  system_state_id TEXT,
  team TEXT,
  side TEXT,
  gsis_id TEXT,
  snaps INT,
  PRIMARY KEY (system_state_id, team, side, gsis_id)
);

CREATE INDEX IF NOT EXISTS idx_player_snaps_state ON player_snaps_in_state(system_state_id, team, side, gsis_id);
CREATE INDEX IF NOT EXISTS idx_player_snaps_state_only ON player_snaps_in_state(system_state_id, team, side);

CREATE TABLE IF NOT EXISTS co_snaps (
  system_state_id TEXT,
  team TEXT,
  side TEXT,
  a_gsis TEXT,
  b_gsis TEXT,
  co_snaps INT,
  PRIMARY KEY (system_state_id, team, side, a_gsis, b_gsis)
);

CREATE INDEX IF NOT EXISTS idx_co_snaps_state ON co_snaps(system_state_id, team, side);

CREATE TABLE IF NOT EXISTS player_role_counts_in_state (
  system_state_id TEXT,
  team TEXT,
  side TEXT,
  gsis_id TEXT,
  role TEXT,
  snaps INT,
  PRIMARY KEY (system_state_id, team, side, gsis_id, role)
);

CREATE INDEX IF NOT EXISTS idx_role_counts_state ON player_role_counts_in_state(system_state_id, team, side, gsis_id);

CREATE TABLE IF NOT EXISTS role_pair_weights (
  side TEXT,
  role_a TEXT,
  role_b TEXT,
  weight NUMERIC,
  PRIMARY KEY (side, role_a, role_b)
);

-- Seed default weights if table is empty
INSERT INTO role_pair_weights (side, role_a, role_b, weight)
SELECT vals.side, vals.role_a, vals.role_b, vals.weight
FROM (
  VALUES
    ('offense','OL','OL',1.00),
    ('offense','OL','QB',0.80),
    ('offense','QB','OL',0.80),
    ('offense','QB','WR',0.85),
    ('offense','WR','QB',0.85),
    ('offense','QB','TE',0.80),
    ('offense','TE','QB',0.80),
    ('offense','QB','RB',0.70),
    ('offense','RB','QB',0.70),
    ('offense','WR','TE',0.50),
    ('offense','TE','WR',0.50),
    ('offense','WR','WR',0.40),
    ('offense','TE','OL',0.70),
    ('offense','OL','TE',0.70),
    ('offense','RB','OL',0.70),
    ('offense','OL','RB',0.70),
    ('offense','RB','TE',0.55),
    ('offense','TE','RB',0.55),
    ('offense','RB','WR',0.40),
    ('offense','WR','RB',0.40),
    ('defense','DL','DL',1.00),
    ('defense','DL','LB',0.85),
    ('defense','LB','DL',0.85),
    ('defense','LB','LB',0.80),
    ('defense','CB','S',0.80),
    ('defense','S','CB',0.80),
    ('defense','CB','CB',0.60),
    ('defense','S','S',0.60),
    ('defense','DL','CB',0.50),
    ('defense','CB','DL',0.50),
    ('defense','LB','CB',0.55),
    ('defense','CB','LB',0.55),
    ('defense','LB','S',0.65),
    ('defense','S','LB',0.65),
    ('defense','DL','S',0.55),
    ('defense','S','DL',0.55)
) AS vals(side, role_a, role_b, weight)
ON CONFLICT DO NOTHING;

