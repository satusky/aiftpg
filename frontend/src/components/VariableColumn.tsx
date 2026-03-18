import { useMemo } from 'react';
import { Stack, Title, Box } from '@mantine/core';
import type { LeaderboardEntry, MetricKey } from '../types';
import TeamCard from './TeamCard';

interface Props {
  variableId: string;
  entries: LeaderboardEntry[];
  sortMetric: MetricKey;
}

export default function VariableColumn({ variableId, entries, sortMetric }: Props) {
  const sorted = useMemo(() => {
    return [...entries]
      .sort((a, b) => (b[sortMetric] ?? -1) - (a[sortMetric] ?? -1))
      .map((e, i) => ({ ...e, rank: i + 1 }));
  }, [entries, sortMetric]);

  return (
    <Box miw={280} maw={320}>
      <Title order={4} mb="sm">
        {variableId}
      </Title>
      <Stack gap="sm">
        {sorted.map((entry) => (
          <TeamCard key={entry.team_name} entry={entry} sortMetric={sortMetric} />
        ))}
      </Stack>
    </Box>
  );
}
