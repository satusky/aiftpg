import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { SubmissionRecord } from '../types';

interface Props {
  submissions: SubmissionRecord[];
  variableId: string;
}

export default function ScoreChart({ submissions, variableId }: Props) {
  const data = submissions.map((s, i) => ({
    index: i + 1,
    label: s.submitted_at ? new Date(s.submitted_at).toLocaleString() : `#${i + 1}`,
    F1: s.f1,
    Accuracy: s.accuracy,
    Precision: s.precision,
    Recall: s.recall,
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="index" label={{ value: 'Submission #', position: 'insideBottom', offset: -2 }} />
          <YAxis domain={[0, 1]} label={{ value: 'Score', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            labelFormatter={(val) => {
              const d = data[Number(val) - 1];
              return d ? d.label : `Submission ${val}`;
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="F1" stroke="#0077b6" dot={false} name={`F1 - ${variableId}`} />
          <Line type="monotone" dataKey="Accuracy" stroke="#2a9d8f" dot={false} name="Accuracy" />
          <Line type="monotone" dataKey="Precision" stroke="#e9c46a" dot={false} name="Precision" />
          <Line type="monotone" dataKey="Recall" stroke="#e76f51" dot={false} name="Recall" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
