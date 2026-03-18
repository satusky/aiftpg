# Hackathon Submission & Scoring Platform

A platform for running hackathon-style competitions where teams submit extracted values against ground truth data. Submissions are automatically scored on accuracy, precision, recall, and F1, with results displayed on a live leaderboard.

## Architecture

- **Backend**: FastAPI (async) with SQLAlchemy + SQLite (aiosqlite)
- **Frontend**: React + Mantine UI, built with Vite
- **Package management**: [uv](https://docs.astral.sh/uv/)

## Setup

```bash
# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend && npm install
```

## Running

```bash
# Start the backend (serves API and built frontend)
uv run uvicorn app.main:app --reload

# In a separate terminal, start the frontend dev server (optional, for development)
cd frontend && npm run dev
```

The API is available at `http://localhost:8000` and OpenAPI docs at `http://localhost:8000/docs`.

## API Endpoints

### Submissions
- `POST /api/submissions` — Submit extracted values for scoring
- `GET /api/submissions` — List submissions (filterable by `team_name`, `variable_id`)
- `GET /api/submissions/{id}` — Get a single submission

### Ground Truth
- `POST /api/ground-truth/upload` — Upload ground truth CSV/JSON for a variable
- `GET /api/ground-truth` — List variables with ground truth loaded
- `DELETE /api/ground-truth/{variable_id}` — Delete ground truth for a variable
- `POST /api/ground-truth/rescore` — Recompute all submission scores against current ground truth

### Leaderboard
- `GET /api/leaderboard` — Best score per team per variable, ranked by F1
- `GET /api/leaderboard/overall` — Average best F1 across variables per team
- `GET /api/teams` — List all teams
- `GET /api/teams/{team_name}` — Team detail with per-variable submission history

## Scoring

Submissions are scored against ground truth by document ID. Values are compared with case-insensitive string matching and numeric coercion. Metrics computed: accuracy, precision, recall, and F1.

## Simulating Teams

A script is included to simulate 5 teams submitting across multiple rounds:

```bash
# Start the server first, then:
uv run python scripts/simulate_teams.py
```

## Testing

```bash
uv run pytest tests/ -v
```

## Configuration

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///data/hackathon.db` | Database connection string |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
