"use client";

import { RosterPlayer } from "../lib/types";
import { cn } from "../lib/utils";

interface Props {
  lineup: RosterPlayer[];
  onRemove: (gsisId: string) => void;
  onSwap: (fromIndex: number, toIndex: number) => void;
}

export function LineupSlots({ lineup, onRemove, onSwap }: Props) {
  const status =
    lineup.length === 11
      ? { message: "Lineup locked in", tone: "text-emerald-600" }
      : { message: `Select ${11 - lineup.length} more players`, tone: "text-amber-600" };

  return (
    <div className="card flex w-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Lineup ({lineup.length}/11)</h2>
        <span className={cn("text-xs font-medium", status.tone)}>{status.message}</span>
      </div>
      <ol className="grid gap-3 md:grid-cols-2">
        {Array.from({ length: 11 }).map((_, index) => {
          const player = lineup[index];
          return (
            <li
              key={index}
              className={cn(
                "flex items-center justify-between rounded-2xl border px-4 py-3",
                player ? "border-primary/30 bg-primary/5" : "border-dashed border-slate-300 bg-transparent"
              )}
            >
              {player ? (
                <>
                  <div>
                    <div className="font-medium">{player.name}</div>
                    <div className="text-xs text-slate-500">
                      {player.position_group ?? player.position ?? ""} · {player.gsis_id}
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      className="rounded-full border border-slate-200 px-2 py-1 text-xs"
                      onClick={() => onSwap(index, Math.max(index - 1, 0))}
                      disabled={index === 0}
                    >
                      ↑
                    </button>
                    <button
                      type="button"
                      className="rounded-full border border-slate-200 px-2 py-1 text-xs"
                      onClick={() => onSwap(index, Math.min(index + 1, 10))}
                      disabled={index === lineup.length - 1 || index === 10}
                    >
                      ↓
                    </button>
                    <button
                      type="button"
                      className="rounded-full bg-white px-2 py-1 text-xs font-medium text-red-500"
                      onClick={() => onRemove(player.gsis_id)}
                    >
                      Remove
                    </button>
                  </div>
                </>
              ) : (
                <span className="text-sm text-slate-400">Slot {index + 1}</span>
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

