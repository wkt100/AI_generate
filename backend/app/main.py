from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import Config
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Config.ensure_dirs()
    await init_db()
    yield


app = FastAPI(title="Edict API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Edict API"}
