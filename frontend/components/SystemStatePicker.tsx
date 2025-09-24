"use client";

import { Side, SystemStateLabel } from "../lib/types";

interface Props {
  seasons: number[];
  selectedSeason?: number;
  onSeasonChange: (season: number) => void;
  teams: string[];
  selectedTeam?: string;
  onTeamChange: (team: string) => void;
  side: Side;
  onSideChange: (side: Side) => void;
  systemStates: SystemStateLabel[];
  systemStateId?: string;
  onSystemStateChange: (id: string) => void;
}

export function SystemStatePicker({
  seasons,
  selectedSeason,
  onSeasonChange,
  teams,
  selectedTeam,
  onTeamChange,
  side,
  onSideChange,
  systemStates,
  systemStateId,
  onSystemStateChange
}: Props) {
  return (
    <div className="card flex flex-col gap-4">
      <h2 className="text-lg font-semibold">Context</h2>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="flex flex-col gap-2">
          <label className="text-xs font-medium uppercase text-slate-500">Season</label>
          <select
            className="rounded-xl border border-slate-200 bg-white px-3 py-2"
            value={selectedSeason ?? ""}
            onChange={(e) => onSeasonChange(Number(e.target.value))}
          >
            <option value="" disabled>
              Select season
            </option>
            {seasons.map((season) => (
              <option key={season} value={season}>
                {season}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs font-medium uppercase text-slate-500">Team</label>
          <select
            className="rounded-xl border border-slate-200 bg-white px-3 py-2"
            value={selectedTeam ?? ""}
            onChange={(e) => onTeamChange(e.target.value)}
            disabled={!teams.length}
          >
            <option value="" disabled>
              Select team
            </option>
            {teams.map((team) => (
              <option key={team} value={team}>
                {team}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs font-medium uppercase text-slate-500">Side</label>
          <div className="flex gap-2">
            {(["offense", "defense"] as Side[]).map((candidate) => (
              <button
                key={candidate}
                type="button"
                onClick={() => onSideChange(candidate)}
                className={`flex-1 rounded-full px-3 py-2 text-sm font-medium transition ${
                  side === candidate ? "bg-primary text-white" : "bg-white text-slate-600 hover:bg-slate-100"
                }`}
              >
                {candidate === "offense" ? "Offense" : "Defense"}
              </button>
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs font-medium uppercase text-slate-500">System State</label>
          <select
            className="rounded-xl border border-slate-200 bg-white px-3 py-2"
            value={systemStateId ?? ""}
            onChange={(e) => onSystemStateChange(e.target.value)}
            disabled={!systemStates.length}
          >
            <option value="" disabled>
              Select window
            </option>
            {systemStates.map((state) => (
              <option key={state.system_state_id} value={state.system_state_id}>
                {state.coach_name ?? state.coach_id} · {state.role ?? "Play Caller"}
              </option>
            ))}
          </select>
          {systemStateId && (
            <p className="text-xs text-slate-500">
              {systemStates.find((s) => s.system_state_id === systemStateId)?.total_snaps ?? 0} snaps logged
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

