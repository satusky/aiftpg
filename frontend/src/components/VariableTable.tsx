import { Table, Badge, Anchor } from '@mantine/core';
import { Link } from 'react-router-dom';
import type { LeaderboardEntry } from '../types';
import { medalColor } from '../constants';

interface Props {
  entries: LeaderboardEntry[];
}

function fmt(v: number | null) {
  return v != null ? v.toFixed(4) : 'N/A';
}

export default function VariableTable({ entries }: Props) {
  return (
    <Table striped highlightOnHover>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Rank</Table.Th>
          <Table.Th>Team</Table.Th>
          <Table.Th>Best F1</Table.Th>
          <Table.Th>Accuracy</Table.Th>
          <Table.Th>Precision</Table.Th>
          <Table.Th>Recall</Table.Th>
          <Table.Th>Submissions</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {entries.map((e) => (
          <Table.Tr key={e.team_name}>
            <Table.Td>
              {medalColor[e.rank] ? (
                <Badge color={medalColor[e.rank]} variant="filled">
                  {e.rank}
                </Badge>
              ) : (
                e.rank
              )}
            </Table.Td>
            <Table.Td>
              <Anchor component={Link} to={`/teams/${encodeURIComponent(e.team_name)}`}>
                {e.team_name}
              </Anchor>
            </Table.Td>
            <Table.Td ff="monospace">{fmt(e.best_f1)}</Table.Td>
            <Table.Td ff="monospace">{fmt(e.best_accuracy)}</Table.Td>
            <Table.Td ff="monospace">{fmt(e.best_precision)}</Table.Td>
            <Table.Td ff="monospace">{fmt(e.best_recall)}</Table.Td>
            <Table.Td>{e.submission_count}</Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
}
