"""Simulate 5 teams submitting results to the live server.

Usage:
    1. Start the server:  .venv/bin/uvicorn app.main:app --reload
    2. Run this script:   .venv/bin/python scripts/simulate_teams.py
"""

import asyncio
import csv
import io
import random
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000"
TEAM_NAMES = ["Team Alpha", "Team Beta", "Team Gamma", "Team Delta", "Team Epsilon"]
VARIABLES = {
    "cancer": {"possible_values": ["YES", "NO", "MAYBE"]},
    "tissue": {"possible_values": ["breast", "liver", "colon", "lung", "none"]},
    "laterality": {"possible_values": ["right", "left", "both", "none"]},
}
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "ground_truth_full.csv"
NUM_ROUNDS = 5
DELAY_SECONDS = 10


def load_ground_truth() -> dict[str, dict[str, str]]:
    """Return {variable_name: {doc_id: value}} for each variable."""
    gt: dict[str, dict[str, str]] = {var: {} for var in VARIABLES}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_id = row["document_id"]
            for var in VARIABLES:
                gt[var][doc_id] = row[var]
    return gt


def ground_truth_csv_bytes(var_gt: dict[str, str]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["document_id", "value"])
    for doc_id, value in var_gt.items():
        writer.writerow([doc_id, value])
    return buf.getvalue().encode()


def build_submission(
    var_gt: dict[str, str],
    possible_values: list[str],
    correctness: float,
    rng: random.Random,
) -> dict[str, str]:
    extracted: dict[str, str] = {}
    for doc_id, truth in var_gt.items():
        if rng.random() < correctness:
            extracted[doc_id] = truth
        else:
            wrong_choices = [v for v in possible_values if v != truth]
            extracted[doc_id] = rng.choice(wrong_choices)
    return extracted


async def main():
    gt = load_ground_truth()
    num_docs = len(next(iter(gt.values())))
    print(f"Loaded {num_docs} documents for {len(VARIABLES)} variables from ground_truth_full.csv")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Step 1 — upload ground truth for each variable
        print("Uploading ground truth...")
        for var_name, var_gt in gt.items():
            gt_csv = ground_truth_csv_bytes(var_gt)
            resp = await client.post(
                "/api/ground-truth/upload",
                files={"file": ("ground_truth.csv", gt_csv, "text/csv")},
                data={"variable_id": var_name},
            )
            resp.raise_for_status()
            print(f"  {var_name}: {resp.json()}")

        # Step 2 — assign random correctness per team
        rng = random.Random(42)
        team_correctness: dict[str, float] = {}
        for name in TEAM_NAMES:
            team_correctness[name] = round(rng.uniform(0.3, 0.95), 2)

        print("\nTeam correctness rates:")
        for name, pct in team_correctness.items():
            print(f"  {name}: {pct:.0%}")

        # Step 3 — submit multiple rounds, all 5 teams × all variables concurrently
        async def submit(team_name: str, var_name: str, round_num: int) -> dict:
            seed = hash((team_name, var_name, round_num))
            extracted = build_submission(
                gt[var_name],
                VARIABLES[var_name]["possible_values"],
                team_correctness[team_name],
                random.Random(seed),
            )
            payload = {
                "team_name": team_name,
                "variable_id": var_name,
                "extracted_values": extracted,
            }
            r = await client.post("/api/submissions", json=payload)
            r.raise_for_status()
            return r.json()

        for round_num in range(1, NUM_ROUNDS + 1):
            print(f"\n--- Round {round_num}/{NUM_ROUNDS} ---")
            results = await asyncio.gather(
                *(
                    submit(name, var_name, round_num)
                    for name in TEAM_NAMES
                    for var_name in VARIABLES
                )
            )

            for res in results:
                print(
                    f"  {res['team_name']:15s}  {res['variable_id']:12s}  "
                    f"accuracy={res['accuracy']:.3f}  "
                    f"precision={res['precision']:.3f}  "
                    f"recall={res['recall']:.3f}  "
                    f"f1={res['f1']:.3f}"
                )

            if round_num < NUM_ROUNDS:
                print(f"\nWaiting {DELAY_SECONDS}s before next round...")
                await asyncio.sleep(DELAY_SECONDS)

        # Print final leaderboard
        lb_resp = await client.get("/api/leaderboard")
        lb_resp.raise_for_status()
        lb = lb_resp.json()
        print("\n=== Final Leaderboard ===")
        for entry in lb:
            print(f"  #{entry['rank']} {entry['team_name']:15s}  best_f1={entry['best_f1']:.3f}")

        print(f"\nDone! View the dashboard at {BASE_URL}/dashboard/")


if __name__ == "__main__":
    asyncio.run(main())
