import { Table, Badge, Anchor } from '@mantine/core';
import { Link } from 'react-router-dom';
import type { OverallLeaderboardEntry } from '../types';
import { medalColor } from '../constants';

interface Props {
  data: OverallLeaderboardEntry[];
}

export default function OverallTable({ data }: Props) {
  return (
    <Table striped highlightOnHover>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Rank</Table.Th>
          <Table.Th>Team</Table.Th>
          <Table.Th>Avg Best F1</Table.Th>
          <Table.Th>Variables</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {data.map((entry) => (
          <Table.Tr key={entry.team_name}>
            <Table.Td>
              {medalColor[entry.rank] ? (
                <Badge color={medalColor[entry.rank]} variant="filled">
                  {entry.rank}
                </Badge>
              ) : (
                entry.rank
              )}
            </Table.Td>
            <Table.Td>
              <Anchor component={Link} to={`/teams/${encodeURIComponent(entry.team_name)}`}>
                {entry.team_name}
              </Anchor>
            </Table.Td>
            <Table.Td ff="monospace">
              {entry.avg_best_f1 != null ? entry.avg_best_f1.toFixed(4) : 'N/A'}
            </Table.Td>
            <Table.Td>{entry.variables_attempted}</Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
}
