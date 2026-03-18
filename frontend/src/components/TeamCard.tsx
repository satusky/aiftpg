import { Card, Badge, Anchor, Text, Group, Stack } from '@mantine/core';
import { Link } from 'react-router-dom';
import type { LeaderboardEntry, MetricKey } from '../types';
import { medalColor, metricColor, metricLabel } from '../constants';

interface Props {
  entry: LeaderboardEntry;
  sortMetric: MetricKey;
}

function fmt(v: number | null) {
  return v != null ? v.toFixed(2) : 'N/A';
}

const allMetrics: MetricKey[] = ['best_f1', 'best_accuracy', 'best_precision', 'best_recall'];

export default function TeamCard({ entry, sortMetric }: Props) {
  return (
    <Card shadow="sm" padding="sm" radius="md" withBorder>
      <Anchor component={Link} to={`/teams/${encodeURIComponent(entry.team_name)}`} fw={700} size="md" c="var(--mantine-color-text)">
        {entry.team_name}
      </Anchor>

      <Group gap="xs" mt={4} mb="xs">
        {medalColor[entry.rank] ? (
          <Badge color={medalColor[entry.rank]} variant="filled" size="sm">
            #{entry.rank}
          </Badge>
        ) : (
          <Badge variant="default" size="sm">#{entry.rank}</Badge>
        )}
        <Text size="xs" c="dimmed">
          {entry.submission_count} submission{entry.submission_count !== 1 ? 's' : ''}
        </Text>
      </Group>

      <Group align="flex-start" mt="xs" gap="md">
        <div>
          <Badge variant="light" color={metricColor[sortMetric]} size="md">
            {metricLabel[sortMetric]}
          </Badge>
          <Text ff="monospace" fw={700} size="xl">
            {fmt(entry[sortMetric])}
          </Text>
        </div>

        <Stack gap={4}>
          {allMetrics.filter(m => m !== sortMetric).map(m => (
            <Group key={m} gap={6}>
              <Badge variant="light" color={metricColor[m]} size="xs">{metricLabel[m]}</Badge>
              <Text ff="monospace" size="xs">{fmt(entry[m])}</Text>
            </Group>
          ))}
        </Stack>
      </Group>
    </Card>
  );
}
