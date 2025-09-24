import { CoachesActiveResponse, LineupScoreResponse, RosterPlayer, Side, SystemStateLabel, SystemStateSummary } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json"
    },
    ...options,
    cache: options?.method === "GET" ? "no-store" : undefined
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed (${res.status}): ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  seasons: () => request<{ seasons: number[] }>("/meta/seasons"),
  teams: (season: number) => request<{ season: number; teams: string[] }>(`/teams?season=${season}`),
  systemStates: (team: string, side: Side) => request<SystemStateLabel[]>(`/system_state?team=${team}&side=${side}`),
  roster: (team: string, side: Side, systemStateId?: string) => {
    const params = new URLSearchParams({ team, side });
    if (systemStateId) params.append("system_state_id", systemStateId);
    return request<RosterPlayer[]>(`/roster?${params.toString()}`);
  },
  scoreLineup: (payload: { team: string; side: Side; system_state_id: string; lineup: string[] }) =>
    request<LineupScoreResponse>("/score/lineup", { method: "POST", body: JSON.stringify(payload) }),
  activeCoaches: (team: string, date?: string) => {
    const params = new URLSearchParams({ team });
    if (date) params.append("date", date);
    return request<CoachesActiveResponse>(`/coaches/active?${params.toString()}`);
  },
  systemStateSummary: (team: string, side: Side, systemStateId: string) =>
    request<SystemStateSummary>(
      `/system_state/summary?team=${team}&side=${side}&system_state_id=${encodeURIComponent(systemStateId)}`
    )
};

