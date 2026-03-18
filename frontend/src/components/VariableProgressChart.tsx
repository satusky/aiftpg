import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { SubmissionRecord } from '../types';

interface TeamData {
  teamName: string;
  color: string;
  submissions: SubmissionRecord[];
}

interface Props {
  variableId: string;
  teamsData: TeamData[];
  metricField: string;
}

function LastPointLabel({ cx, cy, index, teamName, color, lastIndex }: {
  cx?: number; cy?: number; index?: number;
  teamName: string; color: string; lastIndex: number;
}) {
  if (index !== lastIndex || cx == null || cy == null) return null;
  return (
    <text x={cx + 8} y={cy + 4} fill={color} fontSize={11} fontWeight={600}>
      {teamName}
    </text>
  );
}

export default function VariableProgressChart({ teamsData, metricField }: Props) {
  const maxLen = Math.max(...teamsData.map(t => t.submissions.length), 0);
  if (maxLen === 0) return null;

  // Build unified data array: { index, [teamName]: value }
  const data: Record<string, number | null | string>[] = [];
  for (let i = 0; i < maxLen; i++) {
    const point: Record<string, number | null | string> = { index: i + 1 };
    for (const t of teamsData) {
      const sub = t.submissions[i];
      point[t.teamName] = sub ? (sub as unknown as Record<string, number | null>)[metricField] : null;
    }
    data.push(point);
  }

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data} margin={{ top: 5, right: 120, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="index"
          label={{ value: 'Submission #', position: 'insideBottom', offset: -2 }}
        />
        <YAxis
          domain={[0, 1]}
          label={{ value: 'Score', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip />
        {teamsData.map((t) => {
          const lastIdx = t.submissions.length;
          return (
            <Line
              key={t.teamName}
              type="monotone"
              dataKey={t.teamName}
              stroke={t.color}
              connectNulls
              dot={(props: Record<string, unknown>) => {
                const { cx, cy, index: idx, key } = props as {
                  cx: number; cy: number; index: number; key: string;
                };
                return (
                  <g key={key}>
                    <circle cx={cx} cy={cy} r={3} fill={t.color} />
                    <LastPointLabel
                      cx={cx} cy={cy} index={idx + 1}
                      teamName={t.teamName} color={t.color} lastIndex={lastIdx}
                    />
                  </g>
                );
              }}
            />
          );
        })}
      </LineChart>
    </ResponsiveContainer>
  );
}
