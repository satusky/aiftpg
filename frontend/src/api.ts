import type { LeaderboardEntry, TeamDetail } from './types';

const BASE = '/api';

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const fetchLeaderboard = () =>
  fetchJson<LeaderboardEntry[]>(`${BASE}/leaderboard`);

export const fetchTeamDetail = (teamName: string) =>
  fetchJson<TeamDetail>(`${BASE}/teams/${encodeURIComponent(teamName)}`);
