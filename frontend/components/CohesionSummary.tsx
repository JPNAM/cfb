"use client";

import { LineupScoreResponse } from "../lib/types";
import { formatNumber } from "../lib/utils";

interface Props {
  score?: LineupScoreResponse;
  loading?: boolean;
}

const metrics = [
  { key: "LSU", label: "System Understanding" },
  { key: "LIU", label: "Individual Understanding" },
  { key: "LIC", label: "Interpersonal Understanding" }
] as const;

export function CohesionSummary({ score, loading }: Props) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-4 w-24 rounded-full bg-slate-200" />
        <div className="mt-4 h-32 rounded-2xl bg-slate-100" />
      </div>
    );
  }

  if (!score) {
    return (
      <div className="card text-sm text-slate-500">
        Choose 11 players and compute cohesion to see results here.
      </div>
    );
  }

  return (
    <div className="card flex flex-col gap-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Cohesion Score</h2>
          <p className="text-sm text-slate-500">Weighted blend of system, individual and interpersonal understanding.</p>
        </div>
        <div className="flex items-end gap-4">
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-primary/10 text-2xl font-semibold text-primary">
            {formatNumber(score.cohesion, 3)}
          </div>
          <div className="space-y-2">
            {metrics.map((metric) => (
              <MetricBar key={metric.key} label={metric.label} value={score[metric.key]} />
            ))}
          </div>
        </div>
      </div>

      {score.playcaller_label && (
        <div className="rounded-2xl bg-primary/10 px-4 py-3 text-sm text-primary">
          Active play-caller window: {score.playcaller_label}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Players</h3>
          <div className="mt-2 space-y-2">
            {score.per_player.map((player) => (
              <div key={player.gsis_id} className="flex items-center justify-between rounded-xl border border-slate-100 px-3 py-2">
                <div>
                  <div className="text-sm font-medium">{player.gsis_id}</div>
                  <div className="text-xs text-slate-500">IUS {formatNumber(player.ius)}</div>
                </div>
                <div className="text-sm font-semibold">{player.snaps_in_state} snaps</div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Top pairings</h3>
          <div className="mt-2 space-y-2">
            {score.pair_edges.slice(0, 6).map((edge) => (
              <div key={`${edge.a}-${edge.b}`} className="rounded-xl border border-slate-100 px-3 py-2 text-sm">
                <div className="font-medium">
                  {edge.a} ↔ {edge.b}
                </div>
                <div className="text-xs text-slate-500">
                  Jaccard {formatNumber(edge.jaccard, 3)} · {edge.co_snaps} co-snaps (w={formatNumber(edge.weight, 2)})
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {score.warnings.length > 0 && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          <strong>Warnings:</strong>
          <ul className="list-inside list-disc">
            {score.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function MetricBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-40 text-xs font-medium text-slate-500">{label}</span>
      <div className="h-2 flex-1 rounded-full bg-slate-200">
        <div className="h-2 rounded-full bg-primary" style={{ width: `${Math.min(100, value * 100)}%` }} />
      </div>
      <span className="w-12 text-right text-sm font-semibold">{formatNumber(value)}</span>
    </div>
  );
}

