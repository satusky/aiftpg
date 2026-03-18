import { Card, Badge, Anchor, Text, Group, SimpleGrid } from '@mantine/core';
import { Link } from 'react-router-dom';
import type { LeaderboardEntry, MetricKey } from '../types';
import { medalColor, metricLabel } from '../constants';

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

      <SimpleGrid cols={2} spacing="xs">
        {allMetrics.map((m) => {
          const isActive = m === sortMetric;
          return (
            <div key={m}>
              <Text size="xs" c="dimmed">{metricLabel[m]}</Text>
              <Text ff="monospace" fw={isActive ? 700 : 400} size={isActive ? 'lg' : 'sm'}>
                {fmt(entry[m])}
              </Text>
            </div>
          );
        })}
      </SimpleGrid>
    </Card>
  );
}
