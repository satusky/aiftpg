import { useMemo, useState } from 'react';
import { Title, Text, Loader, Alert, Stack, SegmentedControl } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { fetchLeaderboard } from '../api';
import KanbanBoard from '../components/KanbanBoard';
import { metricLabel } from '../constants';
import type { LeaderboardEntry, MetricKey } from '../types';

const metricOptions: MetricKey[] = ['best_f1', 'best_accuracy', 'best_precision', 'best_recall'];

export default function LeaderboardPage() {
  const [sortMetric, setSortMetric] = useState<MetricKey>('best_f1');

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

  if (perVar.isLoading) return <Loader m="xl" />;
  if (perVar.error) {
    return <Alert color="red" title="Error">Failed to load leaderboard data.</Alert>;
  }

  const hasData = Object.keys(grouped).length > 0;

  return (
    <Stack gap="xl">
      <Title>Leaderboard</Title>

      {!hasData && <Text c="dimmed">No submissions yet. Submit results via the API to see the leaderboard.</Text>}

      {hasData && (
        <>
          <SegmentedControl
            value={sortMetric}
            onChange={(v) => setSortMetric(v as MetricKey)}
            data={metricOptions.map((k) => ({ label: metricLabel[k], value: k }))}
          />
          <KanbanBoard grouped={grouped} sortMetric={sortMetric} />
        </>
      )}
    </Stack>
  );
}
