# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Backend
uv sync                              # Install/sync Python dependencies
uv run uvicorn app.main:app --reload  # Start dev server on :8000
uv run pytest tests/ -v               # Run all tests
uv run pytest tests/test_scoring.py::TestComputeMetrics::test_perfect_score  # Single test

# Frontend (from frontend/)
npm install                           # Install JS dependencies
npm run dev                           # Vite dev server (proxies /api to :8000)
npm run build                         # TypeScript check + Vite production build
npm run lint                          # ESLint
```

## Architecture

Full-stack hackathon scoring platform: teams submit extracted values per variable, scored automatically against uploaded ground truth.

**Backend**: FastAPI (async) + SQLAlchemy + SQLite (aiosqlite). Database auto-created on startup via `create_all`. All endpoints are under `/api/`. The built frontend is served as static files at `/` when `frontend/dist/` exists.

**Frontend**: React 19 + Mantine UI + TanStack Query + Recharts, built with Vite. API calls go through `frontend/src/api.ts`. Vite dev server proxies `/api` to the backend.

**Scoring** (`app/scoring.py`): Compares submitted values to ground truth by document ID. Values matched case-insensitively with numeric coercion. Computes accuracy, precision, recall, F1.

**Key data flow**: Ground truth uploaded per variable → teams POST submissions → `compute_metrics` scores immediately → leaderboard endpoints aggregate best scores via SQL.

## Data Model

Four SQLAlchemy models in `app/models.py`: `Team`, `Variable`, `GroundTruth`, `Submission`. Submissions belong to a team and variable, storing extracted values (JSON) and computed metrics.

Pydantic schemas in `app/schemas.py` mirror the models for API request/response validation. Leaderboard endpoints use `response_model` with typed schemas (`LeaderboardEntry`, `TeamDetailResponse`, etc.).

## Testing

Tests use `pytest-asyncio` with `asyncio_mode = "auto"`. The `conftest.py` provides two fixtures:
- `session`: in-memory SQLite database, created/destroyed per test
- `client`: `httpx.AsyncClient` with ASGI transport, FastAPI dependency override

The integration test (`test_integration_async_teams.py`) uses a file-based SQLite DB and manages its own engine/session lifecycle independently of conftest.

## Configuration

Environment variables (defaults in `app/config.py`): `DATABASE_URL` (default: `sqlite+aiosqlite:///data/hackathon.db`), `HOST` (`0.0.0.0`), `PORT` (`8000`).
