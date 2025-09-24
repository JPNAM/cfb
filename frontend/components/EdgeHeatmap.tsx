"use client";

import { PairEdge, RosterPlayer } from "../lib/types";
import { formatNumber } from "../lib/utils";

interface Props {
  edges: PairEdge[];
  lineup: RosterPlayer[];
}

export function EdgeHeatmap({ edges, lineup }: Props) {
  if (!edges.length || lineup.length === 0) {
    return null;
  }

  const matrix = new Map<string, PairEdge>();
  edges.forEach((edge) => {
    matrix.set(`${edge.a}-${edge.b}`, edge);
    matrix.set(`${edge.b}-${edge.a}`, edge);
  });

  const ids = lineup.map((p) => p.gsis_id);

  return (
    <div className="card">
      <h3 className="text-lg font-semibold">Chemistry Map</h3>
      <div className="mt-4 overflow-x-auto">
        <table className="border-collapse">
          <thead>
            <tr>
              <th className="sticky left-0 bg-slate-50 px-2 py-1 text-left text-xs font-semibold text-slate-500">Player</th>
              {ids.map((id) => (
                <th key={id} className="px-2 py-1 text-xs font-semibold text-slate-500">
                  {id}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ids.map((rowId, rowIdx) => (
              <tr key={rowId}>
                <th className="sticky left-0 bg-slate-50 px-2 py-1 text-xs font-semibold text-slate-500">{rowId}</th>
                {ids.map((colId, colIdx) => {
                  if (rowIdx === colIdx) {
                    return <td key={colId} className="h-10 w-10 text-center text-xs text-slate-400">—</td>;
                  }
                  const edge = matrix.get(`${rowId}-${colId}`);
                  const value = edge ? edge.jaccard : 0;
                  const bg = `rgba(11, 110, 254, ${value})`;
                  return (
                    <td
                      key={colId}
                      className="h-10 w-10 cursor-pointer text-center text-xs text-white"
                      style={{ backgroundColor: bg }}
                      title={edge ? `${rowId} ↔ ${colId}\nJaccard ${formatNumber(edge.jaccard, 3)}\nCo-snaps ${edge.co_snaps}` : "No overlap"}
                    >
                      {formatNumber(value, 2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

