from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.ground_truth import parse_ground_truth
from app.models import GroundTruth, Submission, Team, Variable
from app.schemas import GroundTruthInfo
from app.scoring import compute_metrics

router = APIRouter(prefix="/api/ground-truth", tags=["ground-truth"])


async def get_or_create_variable(session: AsyncSession, variable_id: str) -> Variable:
    result = await session.execute(select(Variable).where(Variable.id == variable_id))
    variable = result.scalar_one_or_none()
    if not variable:
        variable = Variable(id=variable_id)
        session.add(variable)
        await session.flush()
    return variable


@router.post("/upload")
async def upload_ground_truth(
    file: UploadFile = File(...),
    variable_id: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()
    filename = file.filename or "data.csv"
    data = parse_ground_truth(content, filename)

    if not data:
        raise HTTPException(status_code=400, detail="No data found in uploaded file")

    variable = await get_or_create_variable(session, variable_id)

    # Delete existing ground truth for this variable
    await session.execute(
        delete(GroundTruth).where(GroundTruth.variable_id == variable.id)
    )

    # Insert new ground truth records
    for doc_id, value in data.items():
        gt = GroundTruth(variable_id=variable.id, document_id=doc_id, value=value)
        session.add(gt)

    await session.commit()

    return {
        "variable_id": variable.id,
        "documents_loaded": len(data),
        "message": f"Ground truth loaded for variable '{variable.id}'",
    }


@router.get("", response_model=list[GroundTruthInfo])
async def list_ground_truth(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(
            Variable.id,
            Variable.name,
            func.count(GroundTruth.id).label("doc_count"),
        )
        .outerjoin(GroundTruth)
        .group_by(Variable.id)
        .having(func.count(GroundTruth.id) > 0)
    )
    rows = result.all()
    return [
        GroundTruthInfo(
            variable_id=row[0],
            variable_name=row[1],
            document_count=row[2],
        )
        for row in rows
    ]


@router.delete("/{variable_id}")
async def delete_ground_truth(
    variable_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        delete(GroundTruth).where(GroundTruth.variable_id == variable_id)
    )
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="No ground truth found for this variable")
    return {"variable_id": variable_id, "deleted": result.rowcount}


@router.post("/rescore")
async def rescore_all(session: AsyncSession = Depends(get_session)):
    """Recompute all submission scores against current ground truth."""
    # Load all ground truth grouped by variable
    gt_result = await session.execute(select(GroundTruth))
    gt_rows = gt_result.scalars().all()

    gt_by_variable: dict[str, dict[str, str | None]] = {}
    for gt in gt_rows:
        gt_by_variable.setdefault(gt.variable_id, {})[gt.document_id] = gt.value

    # Load and rescore all submissions
    sub_result = await session.execute(select(Submission))
    submissions = sub_result.scalars().all()

    updated = 0
    for sub in submissions:
        gt_dict = gt_by_variable.get(sub.variable_id, {})
        metrics = compute_metrics(sub.extracted_values, gt_dict)
        sub.accuracy = metrics["accuracy"]
        sub.precision = metrics["precision"]
        sub.recall = metrics["recall"]
        sub.f1 = metrics["f1"]
        sub.score = metrics["f1"]
        updated += 1

    await session.commit()
    return {"rescored": updated}
