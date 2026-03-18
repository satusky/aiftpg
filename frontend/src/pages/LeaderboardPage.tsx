import { useMemo } from 'react';
import { Title, Text, Loader, Alert, Stack } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { fetchLeaderboard, fetchOverallLeaderboard } from '../api';
import OverallTable from '../components/OverallTable';
import VariableTable from '../components/VariableTable';
import type { LeaderboardEntry } from '../types';

export default function LeaderboardPage() {
  const overall = useQuery({
    queryKey: ['overall'],
    queryFn: fetchOverallLeaderboard,
    refetchInterval: 30_000,
    refetchIntervalInBackground: true,
  });
  const perVar = useQuery({
    queryKey: ['leaderboard'],
    queryFn: fetchLeaderboard,
    refetchInterval: 30_000,
    refetchIntervalInBackground: true,
  });

  const grouped = useMemo(() => {
    if (!perVar.data) return {};
    const m: Record<string, LeaderboardEntry[]> = {};
    for (const e of perVar.data) {
      (m[e.variable_id] ??= []).push(e);
    }
    return m;
  }, [perVar.data]);

  if (overall.isLoading || perVar.isLoading) return <Loader m="xl" />;
  if (overall.error || perVar.error) {
    return <Alert color="red" title="Error">Failed to load leaderboard data.</Alert>;
  }

  const hasData = (overall.data && overall.data.length > 0) || Object.keys(grouped).length > 0;

  return (
    <Stack gap="xl">
      <Title>Leaderboard</Title>

      {!hasData && <Text c="dimmed">No submissions yet. Submit results via the API to see the leaderboard.</Text>}

      {overall.data && overall.data.length > 0 && (
        <>
          <Title order={2}>Overall Rankings</Title>
          <OverallTable data={overall.data} />
        </>
      )}

      {Object.entries(grouped).map(([varId, entries]) => (
        <div key={varId}>
          <Title order={2} mb="sm">Variable: {varId}</Title>
          <VariableTable entries={entries} />
        </div>
      ))}
    </Stack>
  );
}
