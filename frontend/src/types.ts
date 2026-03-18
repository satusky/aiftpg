export interface LeaderboardEntry {
  rank: number;
  team_name: string;
  variable_id: string;
  best_f1: number | null;
  best_accuracy: number | null;
  best_precision: number | null;
  best_recall: number | null;
  submission_count: number;
}

export type MetricKey = 'best_f1' | 'best_accuracy' | 'best_precision' | 'best_recall';

export interface SubmissionRecord {
  id: number;
  f1: number | null;
  accuracy: number | null;
  precision: number | null;
  recall: number | null;
  submitted_at: string | null;
}

export interface TeamVariableSummary {
  variable_id: string;
  best_f1: number | null;
  best_accuracy: number | null;
  best_precision: number | null;
  best_recall: number | null;
  submission_count: number;
  submissions: SubmissionRecord[];
}

export interface TeamDetail {
  team_name: string;
  created_at: string;
  variables: TeamVariableSummary[];
}
