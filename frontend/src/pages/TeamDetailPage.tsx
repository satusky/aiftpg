import { useParams, Link } from 'react-router-dom';
import { Title, Text, Loader, Alert, Stack, Anchor, Group, Badge } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { fetchTeamDetail } from '../api';
import ScoreChart from '../components/ScoreChart';

export default function TeamDetailPage() {
  const { teamName } = useParams<{ teamName: string }>();
  const { data, isLoading, error } = useQuery({
    queryKey: ['team', teamName],
    queryFn: () => fetchTeamDetail(teamName!),
    enabled: !!teamName,
    refetchInterval: 30_000,
    refetchIntervalInBackground: true,
  });

  if (isLoading) return <Loader m="xl" />;
  if (error) return <Alert color="red" title="Error">Failed to load team data.</Alert>;
  if (!data) return null;

  return (
    <Stack gap="xl">
      <div>
        <Anchor component={Link} to="/" mb="xs" display="block">&larr; Back to Leaderboard</Anchor>
        <Title>Team: {data.team_name}</Title>
      </div>

      {data.variables.length === 0 && (
        <Text c="dimmed">No submissions found for this team.</Text>
      )}

      {data.variables.map((v) => (
        <Stack key={v.variable_id} gap="sm">
          <Title order={2}>Variable: {v.variable_id}</Title>
          <Group>
            <Badge size="lg" variant="light">Submissions: {v.submission_count}</Badge>
            {v.best_f1 != null && (
              <Badge size="lg" variant="light" color="blue">
                Best F1: {v.best_f1.toFixed(4)}
              </Badge>
            )}
            {v.best_accuracy != null && (
              <Badge size="lg" variant="light" color="teal">
                Best Accuracy: {v.best_accuracy.toFixed(4)}
              </Badge>
            )}
          </Group>
          <ScoreChart submissions={v.submissions} variableId={v.variable_id} />
        </Stack>
      ))}
    </Stack>
  );
}
