from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import BASE_DIR
from app.database import get_session
from app.models import Submission, Team

router = APIRouter(tags=["leaderboard"])
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/api/leaderboard")
async def leaderboard_json(session: AsyncSession = Depends(get_session)):
    """Best score per team per variable, ranked by F1."""
    # Subquery: best F1 per team per variable
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

    # Group by variable and assign ranks
    entries = []
    current_var = None
    rank = 0
    for row in rows:
        if row[1] != current_var:
            current_var = row[1]
            rank = 0
        rank += 1
        entries.append({
            "rank": rank,
            "team_name": row[0],
            "variable_id": row[1],
            "best_f1": row[2],
            "best_accuracy": row[3],
            "best_precision": row[4],
            "best_recall": row[5],
            "submission_count": row[6],
        })

    return entries


@router.get("/api/leaderboard/overall")
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
        {
            "rank": i + 1,
            "team_name": row[0],
            "avg_best_f1": round(row[1], 6) if row[1] is not None else None,
            "variables_attempted": row[2],
        }
        for i, row in enumerate(rows)
    ]


@router.get("/api/teams")
async def list_teams(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Team).order_by(Team.name))
    teams = result.scalars().all()
    return [{"team_name": t.name, "created_at": t.created_at} for t in teams]


@router.get("/api/teams/{team_name}")
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

    # Group by variable
    by_variable: dict[str, list] = {}
    for sub in submissions:
        by_variable.setdefault(sub.variable_id, []).append(sub)

    variables = []
    for var_id, subs in by_variable.items():
        f1_scores = [s.f1 for s in subs if s.f1 is not None]
        acc_scores = [s.accuracy for s in subs if s.accuracy is not None]
        prec_scores = [s.precision for s in subs if s.precision is not None]
        rec_scores = [s.recall for s in subs if s.recall is not None]

        variables.append({
            "variable_id": var_id,
            "best_f1": max(f1_scores) if f1_scores else None,
            "best_accuracy": max(acc_scores) if acc_scores else None,
            "best_precision": max(prec_scores) if prec_scores else None,
            "best_recall": max(rec_scores) if rec_scores else None,
            "submission_count": len(subs),
            "submissions": [
                {
                    "id": s.id,
                    "f1": s.f1,
                    "accuracy": s.accuracy,
                    "precision": s.precision,
                    "recall": s.recall,
                    "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
                }
                for s in subs
            ],
        })

    return {
        "team_name": team.name,
        "created_at": team.created_at,
        "variables": variables,
    }


# Dashboard HTML routes

@router.get("/dashboard/", response_class=HTMLResponse)
async def dashboard(request: Request, session: AsyncSession = Depends(get_session)):
    # Get per-variable leaderboard
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

    # Group by variable
    variables: dict[str, list] = {}
    for row in rows:
        var_id = row[1]
        variables.setdefault(var_id, [])
        rank = len(variables[var_id]) + 1
        variables[var_id].append({
            "rank": rank,
            "team_name": row[0],
            "best_f1": row[2],
            "best_accuracy": row[3],
            "best_precision": row[4],
            "best_recall": row[5],
            "submission_count": row[6],
        })

    # Overall leaderboard
    overall_sub = (
        select(
            Submission.team_id,
            Submission.variable_id,
            func.max(Submission.f1).label("best_f1"),
        )
        .group_by(Submission.team_id, Submission.variable_id)
        .subquery()
    )

    overall_result = await session.execute(
        select(
            Team.name,
            func.avg(overall_sub.c.best_f1).label("avg_best_f1"),
            func.count(overall_sub.c.variable_id).label("variables_attempted"),
        )
        .join(Team, Team.id == overall_sub.c.team_id)
        .group_by(Team.name)
        .order_by(func.avg(overall_sub.c.best_f1).desc())
    )
    overall_rows = overall_result.all()

    overall = [
        {
            "rank": i + 1,
            "team_name": row[0],
            "avg_best_f1": round(row[1], 4) if row[1] is not None else None,
            "variables_attempted": row[2],
        }
        for i, row in enumerate(overall_rows)
    ]

    return templates.TemplateResponse(
        request, "leaderboard.html",
        {"variables": variables, "overall": overall},
    )


@router.get("/dashboard/teams/{team_name}", response_class=HTMLResponse)
async def dashboard_team_detail(
    request: Request,
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
        by_variable.setdefault(sub.variable_id, []).append({
            "id": sub.id,
            "f1": sub.f1,
            "accuracy": sub.accuracy,
            "precision": sub.precision,
            "recall": sub.recall,
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
        })

    return templates.TemplateResponse(
        request, "team_detail.html",
        {"team_name": team_name, "variables": by_variable},
    )
