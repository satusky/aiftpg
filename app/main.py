from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import ground_truth, leaderboard, submissions


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Hackathon Submission & Scoring Platform", lifespan=lifespan)

app.include_router(submissions.router)
app.include_router(ground_truth.router)
app.include_router(leaderboard.router)


@app.get("/")
async def root():
    return {"message": "Hackathon Platform API", "docs": "/docs", "dashboard": "/dashboard/"}
