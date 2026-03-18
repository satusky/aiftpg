import { useMemo, useState } from 'react';
import { Title, Text, Loader, Alert, Stack, SegmentedControl, Paper, Group } from '@mantine/core';
import { useQuery, useQueries } from '@tanstack/react-query';
import { fetchLeaderboard, fetchTeamDetail } from '../api';
import KanbanBoard from '../components/KanbanBoard';
import VariableProgressChart from '../components/VariableProgressChart';
import { metricLabel, TEAM_COLORS, submissionMetricField } from '../constants';
import type { LeaderboardEntry, MetricKey } from '../types';

const metricOptions: MetricKey[] = ['best_f1', 'best_accuracy', 'best_precision', 'best_recall'];

type ViewMode = 'board' | 'charts';

export default function LeaderboardPage() {
  const [sortMetric, setSortMetric] = useState<MetricKey>('best_f1');
  const [viewMode, setViewMode] = useState<ViewMode>('board');

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

  const teamNames = useMemo(() => {
    if (!perVar.data) return [];
    return [...new Set(perVar.data.map(e => e.team_name))].sort();
  }, [perVar.data]);

  const teamColorMap = useMemo(() => {
    const m: Record<string, string> = {};
    teamNames.forEach((name, i) => {
      m[name] = TEAM_COLORS[i % TEAM_COLORS.length];
    });
    return m;
  }, [teamNames]);

  const variableIds = useMemo(() => Object.keys(grouped).sort(), [grouped]);

  const teamQueries = useQueries({
    queries: teamNames.map(name => ({
      queryKey: ['team', name],
      queryFn: () => fetchTeamDetail(name),
      enabled: viewMode === 'charts',
    })),
  });

  const teamsLoading = viewMode === 'charts' && teamQueries.some(q => q.isLoading);

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
          <Group>
            <SegmentedControl
              value={sortMetric}
              onChange={(v) => setSortMetric(v as MetricKey)}
              data={metricOptions.map((k) => ({ label: metricLabel[k], value: k }))}
            />
            <SegmentedControl
              value={viewMode}
              onChange={(v) => setViewMode(v as ViewMode)}
              data={[
                { label: 'Board', value: 'board' },
                { label: 'Charts', value: 'charts' },
              ]}
            />
          </Group>

          {viewMode === 'board' && (
            <KanbanBoard grouped={grouped} sortMetric={sortMetric} />
          )}

          {viewMode === 'charts' && (
            teamsLoading ? <Loader m="xl" /> : (
              <Stack gap="lg">
                {variableIds.map(varId => {
                  const teamsData = teamNames
                    .map((name, i) => {
                      const detail = teamQueries[i].data;
                      const varSummary = detail?.variables.find(v => v.variable_id === varId);
                      if (!varSummary || varSummary.submissions.length === 0) return null;
                      return {
                        teamName: name,
                        color: teamColorMap[name],
                        submissions: varSummary.submissions,
                      };
                    })
                    .filter((d): d is NonNullable<typeof d> => d !== null);

                  if (teamsData.length === 0) return null;

                  return (
                    <Paper key={varId} p="md" withBorder>
                      <Title order={3} mb="sm">{varId}</Title>
                      <VariableProgressChart
                        variableId={varId}
                        teamsData={teamsData}
                        metricField={submissionMetricField[sortMetric]}
                      />
                    </Paper>
                  );
                })}
              </Stack>
            )
          )}
        </>
      )}
    </Stack>
  );
}
