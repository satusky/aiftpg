from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubmissionCreate(BaseModel):
    model_config = ConfigDict(extra="allow")

    team_name: str
    variable_id: str
    extracted_values: dict[str, str | None]


class SubmissionResponse(BaseModel):
    id: int
    team_name: str
    variable_id: str
    extracted_values: dict[str, str | None]
    extra_fields: dict | None = None
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    score: float | None = None
    submitted_at: datetime


class SubmissionDetail(SubmissionResponse):
    pass


class GroundTruthInfo(BaseModel):
    variable_id: str
    variable_name: str | None = None
    document_count: int


class LeaderboardEntry(BaseModel):
    rank: int
    team_name: str
    variable_id: str
    best_f1: float | None = None
    best_accuracy: float | None = None
    best_precision: float | None = None
    best_recall: float | None = None
    submission_count: int


class OverallLeaderboardEntry(BaseModel):
    rank: int
    team_name: str
    avg_best_f1: float | None = None
    variables_attempted: int


class TeamInfo(BaseModel):
    team_name: str
    created_at: datetime


class TeamVariableSummary(BaseModel):
    variable_id: str
    best_f1: float | None = None
    best_accuracy: float | None = None
    best_precision: float | None = None
    best_recall: float | None = None
    submission_count: int
    submissions: list[SubmissionResponse]
