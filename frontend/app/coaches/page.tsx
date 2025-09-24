"use client";

import { useEffect, useState } from "react";
import { Header } from "../../components/Header";
import { api } from "../../lib/api";
import { CoachesActiveResponse, SystemStateLabel } from "../../lib/types";

export default function CoachesPage() {
  const [season, setSeason] = useState<number | undefined>();
  const [seasons, setSeasons] = useState<number[]>([]);
  const [teams, setTeams] = useState<string[]>([]);
  const [team, setTeam] = useState<string | undefined>();
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [active, setActive] = useState<CoachesActiveResponse | undefined>();
  const [systemStates, setSystemStates] = useState<SystemStateLabel[]>([]);

  useEffect(() => {
    api.seasons().then((res) => setSeasons(res.seasons)).catch((err) => console.error(err));
  }, []);

  useEffect(() => {
    if (!season) return;
    api.teams(season).then((res) => setTeams(res.teams)).catch((err) => console.error(err));
  }, [season]);

  useEffect(() => {
    if (!team) return;
    api.activeCoaches(team, date).then(setActive).catch((err) => console.error(err));
    Promise.all([api.systemStates(team, "offense"), api.systemStates(team, "defense")])
      .then(([offense, defense]) => setSystemStates([...offense, ...defense]))
      .catch((err) => console.error(err));
  }, [team, date]);

  return (
    <main className="flex flex-1 flex-col gap-8">
      <Header />
      <section className="card space-y-4">
        <h2 className="text-lg font-semibold">Coordinator windows</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="text-xs font-semibold uppercase text-slate-500">Season</label>
            <select
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2"
              value={season ?? ""}
              onChange={(e) => setSeason(Number(e.target.value))}
            >
              <option value="" disabled>
                Select season
              </option>
              {seasons.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase text-slate-500">Team</label>
            <select
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2"
              value={team ?? ""}
              onChange={(e) => setTeam(e.target.value)}
              disabled={!teams.length}
            >
              <option value="" disabled>
                Select team
              </option>
              {teams.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase text-slate-500">Date</label>
            <input
              type="date"
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
        </div>
        {active && (
          <div className="grid gap-4 md:grid-cols-2">
            <CoachCard title="Offensive Playcaller" coach={active.offense_playcaller} />
            <CoachCard title="Defensive Playcaller" coach={active.defense_playcaller} />
            <CoachCard title="Offensive Coordinator" coach={active.oc} />
            <CoachCard title="Defensive Coordinator" coach={active.dc} />
          </div>
        )}
      </section>

      {systemStates.length > 0 && (
        <section className="card space-y-4">
          <h3 className="text-lg font-semibold">System state history</h3>
          <table className="table">
            <thead>
              <tr>
                <th className="px-4 py-2">Side</th>
                <th className="px-4 py-2">Coach</th>
                <th className="px-4 py-2">Role</th>
                <th className="px-4 py-2">Window</th>
                <th className="px-4 py-2">Snaps</th>
              </tr>
            </thead>
            <tbody>
              {systemStates.map((state) => (
                <tr key={state.system_state_id}>
                  <td className="px-4 py-2 text-sm font-medium capitalize">{state.side}</td>
                  <td className="px-4 py-2 text-sm">{state.coach_name ?? state.coach_id}</td>
                  <td className="px-4 py-2 text-sm">{state.role ?? "Play Caller"}</td>
                  <td className="px-4 py-2 text-xs text-slate-500">
                    {state.window_start ?? "?"} → {state.window_end ?? "present"}
                  </td>
                  <td className="px-4 py-2 text-sm font-semibold">{state.total_snaps ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <section className="card space-y-3 text-sm text-slate-600">
        <h3 className="text-lg font-semibold">Updating coordinator data</h3>
        <p>
          Edit <code>seeds/coach_roles.csv</code> to add new coordinators or play-caller windows. Run
          <code className="ml-1 rounded bg-slate-100 px-2 py-1">make etl</code> to reload the database.
        </p>
      </section>
    </main>
  );
}

interface CoachCardProps {
  title: string;
  coach?: {
    coach_name: string;
    role: string;
    start_date?: string;
    end_date?: string;
  } | null;
}

function CoachCard({ title, coach }: CoachCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
      <h4 className="text-sm font-semibold uppercase text-slate-500">{title}</h4>
      {coach ? (
        <div className="mt-2 text-sm">
          <div className="font-medium">{coach.coach_name}</div>
          <div className="text-xs text-slate-500">{coach.role}</div>
          <div className="text-xs text-slate-500">
            {coach.start_date ?? "?"} → {coach.end_date ?? "present"}
          </div>
        </div>
      ) : (
        <p className="mt-2 text-xs text-slate-400">No data</p>
      )}
    </div>
  );
}

