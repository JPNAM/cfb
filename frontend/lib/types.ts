export type Side = "offense" | "defense";

export interface SystemStateLabel {
  system_state_id: string;
  team: string;
  side: Side;
  coach_id: string;
  coach_name?: string;
  role?: string;
  window_start?: string;
  window_end?: string;
  total_snaps?: number;
}

export interface RosterPlayer {
  gsis_id: string;
  name: string;
  position?: string;
  position_group?: string;
  snaps_in_state: number;
  ius: number;
  roles_breakdown: Record<string, number>;
  n_system_states_seen: number;
}

export interface PairEdge {
  a: string;
  b: string;
  weight: number;
  jaccard: number;
  co_snaps: number;
  n_i: number;
  n_j: number;
}

export interface PlayerScore {
  gsis_id: string;
  snaps_in_state: number;
  ius: number;
  roles: Record<string, number>;
}

export interface LineupScoreResponse {
  LSU: number;
  LIU: number;
  LIC: number;
  cohesion: number;
  warnings: string[];
  per_player: PlayerScore[];
  pair_edges: PairEdge[];
  playcaller_label?: string;
}

export interface CoachesActiveResponse {
  offense_playcaller?: CoachInfo;
  defense_playcaller?: CoachInfo;
  oc?: CoachInfo;
  dc?: CoachInfo;
}

export interface CoachInfo {
  coach_id: string;
  coach_name: string;
  team: string;
  role: string;
  start_date?: string;
  end_date?: string;
}

export interface SystemStateSummary {
  system_state_id: string;
  team_snaps: number;
  distinct_players: number;
  top_pairs: PairEdge[];
  position_mix: Record<string, number>;
}

