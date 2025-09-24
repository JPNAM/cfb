"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CohesionSummary } from "../../components/CohesionSummary";
import { EdgeHeatmap } from "../../components/EdgeHeatmap";
import { Header } from "../../components/Header";
import { LineupSlots } from "../../components/LineupSlots";
import { RosterTable } from "../../components/RosterTable";
import { SystemStatePicker } from "../../components/SystemStatePicker";
import { api } from "../../lib/api";
import { useLineupStore } from "../../lib/useLineupStore";
import { LineupScoreResponse, RosterPlayer, Side, SystemStateLabel } from "../../lib/types";

export default function BuilderPage() {
  const searchParams = useSearchParams();
  const defaultSide = (searchParams.get("side") as Side) ?? "offense";
  const {
    season,
    setSeason,
    team,
    setTeam,
    side,
    setSide,
    systemStateId,
    setSystemState,
    lineup,
    setLineup
  } = useLineupStore();

  const [seasons, setSeasons] = useState<number[]>([]);
  const [teams, setTeams] = useState<string[]>([]);
  const [systemStates, setSystemStates] = useState<SystemStateLabel[]>([]);
  const [roster, setRoster] = useState<RosterPlayer[]>([]);
  const [loadingScore, setLoadingScore] = useState(false);
  const [score, setScore] = useState<LineupScoreResponse | undefined>();

  useEffect(() => {
    setSide(defaultSide);
  }, [defaultSide, setSide]);

  useEffect(() => {
    api.seasons()
      .then((res) => setSeasons(res.seasons))
      .catch((err) => console.error(err));
  }, []);

  useEffect(() => {
    if (!season) return;
    api.teams(season)
      .then((res) => setTeams(res.teams))
      .catch((err) => console.error(err));
  }, [season]);

  useEffect(() => {
    if (!team) {
      setSystemStates([]);
      return;
    }
    api.systemStates(team, side)
      .then((states) => {
        setSystemStates(states);
        if (!states.find((state) => state.system_state_id === systemStateId)) {
          setSystemState(states[0]?.system_state_id);
        }
      })
      .catch((err) => console.error(err));
  }, [team, side, systemStateId, setSystemState]);

  useEffect(() => {
    if (!team || !systemStateId) {
      setRoster([]);
      return;
    }
    api
      .roster(team, side, systemStateId)
      .then((data) => setRoster(data))
      .catch((err) => console.error(err));
  }, [team, side, systemStateId]);


  useEffect(() => {
    setLineup([]);
  }, [team, side, setLineup]);
  useEffect(() => {
    setScore(undefined);
  }, [team, side, systemStateId]);

  const selectedPlayers = useMemo(() => {
    return lineup
      .map((id) => roster.find((player) => player.gsis_id === id))
      .filter((p): p is RosterPlayer => Boolean(p));
  }, [lineup, roster]);

  const togglePlayer = (gsisId: string) => {
    setScore(undefined);
    if (lineup.includes(gsisId)) {
      setLineup(lineup.filter((id) => id !== gsisId));
    } else if (lineup.length < 11) {
      setLineup([...lineup, gsisId]);
    }
  };

  const handleSwap = (from: number, to: number) => {
    if (from === to) return;
    const next = [...lineup];
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    setLineup(next.slice(0, 11));
  };

  const computeScore = async () => {
    if (!team || !systemStateId || lineup.length !== 11) return;
    setLoadingScore(true);
    try {
      const response = await api.scoreLineup({ team, side, system_state_id: systemStateId, lineup });
      setScore(response);
    } catch (err) {
      console.error(err);
      alert("Failed to compute cohesion. Check API logs.");
    } finally {
      setLoadingScore(false);
    }
  };

  return (
    <main className="flex flex-1 flex-col gap-8">
      <Header />
      <SystemStatePicker
        seasons={seasons}
        selectedSeason={season}
        onSeasonChange={setSeason}
        teams={teams}
        selectedTeam={team}
        onTeamChange={setTeam}
        side={side}
        onSideChange={setSide}
        systemStates={systemStates}
        systemStateId={systemStateId}
        onSystemStateChange={setSystemState}
      />

      <section className="grid gap-6 lg:grid-cols-2">
        <RosterTable roster={roster} selected={lineup} onToggle={togglePlayer} />
        <div className="flex flex-col gap-6">
          <LineupSlots lineup={selectedPlayers} onRemove={togglePlayer} onSwap={handleSwap} />
          <button
            type="button"
            className="btn self-end"
            disabled={lineup.length !== 11 || loadingScore}
            onClick={computeScore}
          >
            {loadingScore ? "Computing…" : "Compute Cohesion"}
          </button>
        </div>
      </section>

      <CohesionSummary score={score} loading={loadingScore} />
      {score && <EdgeHeatmap edges={score.pair_edges} lineup={selectedPlayers} />}
    </main>
  );
}

