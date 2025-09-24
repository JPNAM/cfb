"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Side } from "./types";

interface LineupState {
  season?: number;
  team?: string;
  side: Side;
  systemStateId?: string;
  lineup: string[];
  setSeason: (season: number) => void;
  setTeam: (team: string) => void;
  setSide: (side: Side) => void;
  setSystemState: (id: string | undefined) => void;
  setLineup: (lineup: string[]) => void;
  reset: () => void;
}

const initialState = {
  side: "offense" as Side,
  lineup: [] as string[]
};

export const useLineupStore = create<LineupState>()(
  persist(
    (set) => ({
      ...initialState,
      setSeason: (season) => set({ season }),
      setTeam: (team) => set({ team }),
      setSide: (side) => set({ side, lineup: [] }),
      setSystemState: (systemStateId) => set({ systemStateId }),
      setLineup: (lineup) => set({ lineup }),
      reset: () => set(initialState)
    }),
    {
      name: "cohesion-lineup"
    }
  )
);

