from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Submission, Team
from app.schemas import (
    LeaderboardEntry,
    OverallLeaderboardEntry,
    SubmissionBrief,
    TeamDetailResponse,
    TeamInfo,
    TeamVariableSummary,
)

router = APIRouter(tags=["leaderboard"])


@router.get("/api/leaderboard", response_model=list[LeaderboardEntry])
async def leaderboard_json(session: AsyncSession = Depends(get_session)):
    """Best score per team per variable, ranked by F1."""
    best_sub = (
        select(
            Submission.team_id,
            Submission.variable_id,
            func.max(Submission.f1).label("best_f1"),
            func.max(Submission.accuracy).label("best_accuracy"),
            func.max(Submission.precision).label("best_precision"),
            func.max(Submission.recall).label("best_recall"),
            func.count(Submission.id).label("submission_count"),
        )
        .group_by(Submission.team_id, Submission.variable_id)
        .subquery()
    )

    result = await session.execute(
        select(
            Team.name,
            best_sub.c.variable_id,
            best_sub.c.best_f1,
            best_sub.c.best_accuracy,
            best_sub.c.best_precision,
            best_sub.c.best_recall,
            best_sub.c.submission_count,
        )
        .join(Team, Team.id == best_sub.c.team_id)
        .order_by(best_sub.c.variable_id, best_sub.c.best_f1.desc())
    )
    rows = result.all()

    entries = []
    current_var = None
    rank = 0
    for row in rows:
        if row.variable_id != current_var:
            current_var = row.variable_id
            rank = 0
        rank += 1
        entries.append(LeaderboardEntry(
            rank=rank,
            team_name=row.name,
            variable_id=row.variable_id,
            best_f1=row.best_f1,
            best_accuracy=row.best_accuracy,
            best_precision=row.best_precision,
            best_recall=row.best_recall,
            submission_count=row.submission_count,
        ))

    return entries


@router.get("/api/leaderboard/overall", response_model=list[OverallLeaderboardEntry])
async def overall_leaderboard(session: AsyncSession = Depends(get_session)):
    """Overall leaderboard: average best F1 across variables per team."""
    best_sub = (
        select(
            Submission.team_id,
            Submission.variable_id,
            func.max(Submission.f1).label("best_f1"),
        )
        .group_by(Submission.team_id, Submission.variable_id)
        .subquery()
    )

    result = await session.execute(
        select(
            Team.name,
            func.avg(best_sub.c.best_f1).label("avg_best_f1"),
            func.count(best_sub.c.variable_id).label("variables_attempted"),
        )
        .join(Team, Team.id == best_sub.c.team_id)
        .group_by(Team.name)
        .order_by(func.avg(best_sub.c.best_f1).desc())
    )
    rows = result.all()

    return [
        OverallLeaderboardEntry(
            rank=i + 1,
            team_name=row.name,
            avg_best_f1=round(row.avg_best_f1, 6) if row.avg_best_f1 is not None else None,
            variables_attempted=row.variables_attempted,
        )
        for i, row in enumerate(rows)
    ]


@router.get("/api/teams", response_model=list[TeamInfo])
async def list_teams(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Team).order_by(Team.name))
    teams = result.scalars().all()
    return [TeamInfo(team_name=t.name, created_at=t.created_at) for t in teams]


@router.get("/api/teams/{team_name}", response_model=TeamDetailResponse)
async def team_detail_json(
    team_name: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Team).where(Team.name == team_name))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    subs_result = await session.execute(
        select(Submission)
        .where(Submission.team_id == team.id)
        .order_by(Submission.variable_id, Submission.submitted_at)
    )
    submissions = subs_result.scalars().all()

    by_variable: dict[str, list] = {}
    for sub in submissions:
        by_variable.setdefault(sub.variable_id, []).append(sub)

    variables = []
    for var_id, subs in by_variable.items():
        f1_scores = [s.f1 for s in subs if s.f1 is not None]
        acc_scores = [s.accuracy for s in subs if s.accuracy is not None]
        prec_scores = [s.precision for s in subs if s.precision is not None]
        rec_scores = [s.recall for s in subs if s.recall is not None]

        variables.append(TeamVariableSummary(
            variable_id=var_id,
            best_f1=max(f1_scores) if f1_scores else None,
            best_accuracy=max(acc_scores) if acc_scores else None,
            best_precision=max(prec_scores) if prec_scores else None,
            best_recall=max(rec_scores) if rec_scores else None,
            submission_count=len(subs),
            submissions=[
                SubmissionBrief(
                    id=s.id,
                    f1=s.f1,
                    accuracy=s.accuracy,
                    precision=s.precision,
                    recall=s.recall,
                    submitted_at=s.submitted_at,
                )
                for s in subs
            ],
        ))

    return TeamDetailResponse(
        team_name=team.name,
        created_at=team.created_at,
        variables=variables,
    )
