import { ScrollArea, Group } from '@mantine/core';
import type { LeaderboardEntry, MetricKey } from '../types';
import VariableColumn from './VariableColumn';

interface Props {
  grouped: Record<string, LeaderboardEntry[]>;
  sortMetric: MetricKey;
}

export default function KanbanBoard({ grouped, sortMetric }: Props) {
  const variableIds = Object.keys(grouped).sort();

  return (
    <ScrollArea type="auto">
      <Group align="flex-start" wrap="nowrap" gap="md">
        {variableIds.map((varId) => (
          <VariableColumn
            key={varId}
            variableId={varId}
            entries={grouped[varId]}
            sortMetric={sortMetric}
          />
        ))}
      </Group>
    </ScrollArea>
  );
}
