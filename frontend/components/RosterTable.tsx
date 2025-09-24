"use client";

import { useMemo, useState } from "react";
import { RosterPlayer } from "../lib/types";
import { cn, formatNumber } from "../lib/utils";

interface Props {
  roster: RosterPlayer[];
  selected: string[];
  onToggle: (gsisId: string) => void;
}

export function RosterTable({ roster, selected, onToggle }: Props) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return roster;
    return roster.filter((player) => player.name.toLowerCase().includes(q) || player.gsis_id.includes(q));
  }, [query, roster]);

  return (
    <div className="card flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">Roster</h2>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search players"
          className="w-48 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm"
        />
      </div>
      <div className="max-h-[480px] overflow-y-auto rounded-2xl border border-slate-100">
        <table className="table">
          <thead>
            <tr>
              <th className="px-4 py-3">Player</th>
              <th className="px-4 py-3">Group</th>
              <th className="px-4 py-3 text-right">Snaps</th>
              <th className="px-4 py-3 text-right">IUS</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((player) => {
              const isSelected = selected.includes(player.gsis_id);
              return (
                <tr key={player.gsis_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <div className="font-medium">{player.name}</div>
                    <div className="text-xs text-slate-500">{player.gsis_id}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="badge">{player.position_group ?? player.position ?? "-"}</span>
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-medium">{player.snaps_in_state}</td>
                  <td className="px-4 py-3 text-right text-sm">{formatNumber(player.ius)}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      type="button"
                      className={cn("rounded-full px-3 py-1 text-xs font-medium", isSelected ? "bg-slate-200" : "bg-primary text-white")}
                      onClick={() => onToggle(player.gsis_id)}
                    >
                      {isSelected ? "Selected" : "Add"}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-500">
        Showing {filtered.length} of {roster.length} players. Click to toggle inclusion in the lineup.
      </p>
    </div>
  );
}

