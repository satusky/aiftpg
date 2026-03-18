from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import GroundTruth, Submission, Team, Variable
from app.schemas import SubmissionCreate, SubmissionResponse
from app.scoring import compute_metrics

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


async def get_or_create_team(session: AsyncSession, team_name: str) -> Team:
    result = await session.execute(select(Team).where(Team.name == team_name))
    team = result.scalar_one_or_none()
    if not team:
        team = Team(name=team_name)
        session.add(team)
        await session.flush()
    return team


async def get_or_create_variable(session: AsyncSession, variable_id: str) -> Variable:
    result = await session.execute(select(Variable).where(Variable.id == variable_id))
    variable = result.scalar_one_or_none()
    if not variable:
        variable = Variable(id=variable_id)
        session.add(variable)
        await session.flush()
    return variable


async def get_ground_truth_dict(session: AsyncSession, variable_id: str) -> dict[str, str | None]:
    result = await session.execute(
        select(GroundTruth).where(GroundTruth.variable_id == variable_id)
    )
    rows = result.scalars().all()
    return {row.document_id: row.value for row in rows}


@router.post("", response_model=SubmissionResponse)
async def create_submission(
    body: SubmissionCreate,
    session: AsyncSession = Depends(get_session),
):
    team = await get_or_create_team(session, body.team_name)
    variable = await get_or_create_variable(session, body.variable_id)

    gt_dict = await get_ground_truth_dict(session, variable.id)
    metrics = compute_metrics(body.extracted_values, gt_dict)

    # Collect extra fields
    known_fields = {"team_name", "variable_id", "extracted_values"}
    extra_fields = {k: v for k, v in body.model_extra.items()} if body.model_extra else None

    submission = Submission(
        team_id=team.id,
        variable_id=variable.id,
        extracted_values=body.extracted_values,
        extra_fields=extra_fields,
        accuracy=metrics["accuracy"],
        precision=metrics["precision"],
        recall=metrics["recall"],
        f1=metrics["f1"],
    )
    session.add(submission)
    await session.commit()
    await session.refresh(submission)

    return SubmissionResponse(
        id=submission.id,
        team_name=team.name,
        variable_id=variable.id,
        extracted_values=submission.extracted_values,
        extra_fields=submission.extra_fields,
        accuracy=submission.accuracy,
        precision=submission.precision,
        recall=submission.recall,
        f1=submission.f1,
        submitted_at=submission.submitted_at,
    )


@router.get("", response_model=list[SubmissionResponse])
async def list_submissions(
    team_name: str | None = Query(None),
    variable_id: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    query = select(Submission, Team.name).join(Team)
    if team_name:
        query = query.where(Team.name == team_name)
    if variable_id:
        query = query.where(Submission.variable_id == variable_id)
    query = query.order_by(Submission.submitted_at.desc())

    result = await session.execute(query)
    rows = result.all()

    return [
        SubmissionResponse(
            id=sub.id,
            team_name=tname,
            variable_id=sub.variable_id,
            extracted_values=sub.extracted_values,
            extra_fields=sub.extra_fields,
            accuracy=sub.accuracy,
            precision=sub.precision,
            recall=sub.recall,
            f1=sub.f1,
            submitted_at=sub.submitted_at,
        )
        for sub, tname in rows
    ]


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Submission, Team.name).join(Team).where(Submission.id == submission_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Submission not found")

    sub, tname = row
    return SubmissionResponse(
        id=sub.id,
        team_name=tname,
        variable_id=sub.variable_id,
        extracted_values=sub.extracted_values,
        extra_fields=sub.extra_fields,
        accuracy=sub.accuracy,
        precision=sub.precision,
        recall=sub.recall,
        f1=sub.f1,
        submitted_at=sub.submitted_at,
    )
