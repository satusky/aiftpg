"""Integration test: 5 synthetic teams submit results asynchronously against
ground truth derived from data/ehr_data.csv (Cancer column)."""

import asyncio
import csv
import io
import random
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_session
from app.main import app
from app.models import Base

TEAM_NAMES = ["Team Alpha", "Team Beta", "Team Gamma", "Team Delta", "Team Epsilon"]
VARIABLE_ID = "Cancer"
POSSIBLE_VALUES = ["YES", "NO", "MAYBE"]
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "ehr_data.csv"


def load_ground_truth() -> dict[str, str]:
    """Read ehr_data.csv and return {doc_id: cancer_value} for each row."""
    gt: dict[str, str] = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            doc_id = f"doc_{idx:03d}"
            gt[doc_id] = row["Cancer"]
    return gt


def ground_truth_csv_bytes(gt: dict[str, str]) -> bytes:
    """Serialise ground truth dict to CSV bytes suitable for upload."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["document_id", "value"])
    for doc_id, value in gt.items():
        writer.writerow([doc_id, value])
    return buf.getvalue().encode()


def build_submission(
    gt: dict[str, str], correctness: float, rng: random.Random
) -> dict[str, str]:
    """Build extracted_values where *correctness* fraction of answers are right."""
    extracted: dict[str, str] = {}
    for doc_id, truth in gt.items():
        if rng.random() < correctness:
            extracted[doc_id] = truth
        else:
            wrong_choices = [v for v in POSSIBLE_VALUES if v != truth]
            extracted[doc_id] = rng.choice(wrong_choices)
    return extracted


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_team_submissions():
    """Upload ground truth, submit from 5 teams concurrently, verify scores."""

    # Set up a shared file-based SQLite DB so concurrent sessions work
    engine = create_async_engine("sqlite+aiosqlite:///test_async_teams.db", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            gt = load_ground_truth()
            assert len(gt) > 0, "Ground truth CSV should not be empty"

            # Step 1 — upload ground truth
            gt_csv = ground_truth_csv_bytes(gt)
            resp = await client.post(
                "/api/ground-truth/upload",
                files={"file": ("ground_truth.csv", gt_csv, "text/csv")},
                data={"variable_id": VARIABLE_ID},
            )
            assert resp.status_code == 200
            assert resp.json()["documents_loaded"] == len(gt)

            # Step 2 — prepare team submissions with seeded randomness
            rng = random.Random(42)
            team_correctness: dict[str, float] = {}
            for name in TEAM_NAMES:
                team_correctness[name] = round(rng.uniform(0.3, 0.95), 2)

            # Step 3 — submit all 5 teams concurrently via asyncio.gather
            async def submit(team_name: str) -> dict:
                extracted = build_submission(
                    gt, team_correctness[team_name], random.Random(hash(team_name))
                )
                payload = {
                    "team_name": team_name,
                    "variable_id": VARIABLE_ID,
                    "extracted_values": extracted,
                }
                r = await client.post("/api/submissions", json=payload)
                return {"team_name": team_name, "status": r.status_code, "body": r.json()}

            results = await asyncio.gather(*(submit(name) for name in TEAM_NAMES))

            # Step 4 — assertions on submission responses
            for res in results:
                assert res["status"] == 200, f"{res['team_name']} got status {res['status']}"
                body = res["body"]
                assert body["accuracy"] is not None
                assert body["precision"] is not None
                assert body["recall"] is not None
                assert body["f1"] is not None
                assert 0.0 <= body["f1"] <= 1.0

            # Step 5 — verify leaderboard contains all 5 teams
            lb_resp = await client.get("/api/leaderboard")
            assert lb_resp.status_code == 200
            lb = lb_resp.json()
            lb_teams = {entry["team_name"] for entry in lb}
            for name in TEAM_NAMES:
                assert name in lb_teams, f"{name} missing from leaderboard"

            # Leaderboard should be sorted by best_f1 descending
            f1_scores = [entry["best_f1"] for entry in lb]
            assert f1_scores == sorted(f1_scores, reverse=True)

            # Step 6 — verify overall leaderboard
            overall_resp = await client.get("/api/leaderboard/overall")
            assert overall_resp.status_code == 200
            overall = overall_resp.json()
            overall_teams = {entry["team_name"] for entry in overall}
            for name in TEAM_NAMES:
                assert name in overall_teams, f"{name} missing from overall leaderboard"

            # Step 7 — verify submissions list
            subs_resp = await client.get("/api/submissions")
            assert subs_resp.status_code == 200
            subs = subs_resp.json()
            assert len(subs) == len(TEAM_NAMES)

    finally:
        app.dependency_overrides.clear()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
        # Clean up the test database file
        db_file = Path("test_async_teams.db")
        if db_file.exists():
            db_file.unlink()
