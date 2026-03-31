import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "tasks"

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "minimax")
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

    DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/storage/edict.db"
    STORAGE_PATH = str(STORAGE_DIR)

    MAX_RETRIES = 3
    AGENT_TIMEOUT = 120
    COMMAND_TIMEOUT = 60

    @classmethod
    def ensure_dirs(cls):
        Path(cls.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        Path(cls.STORAGE_PATH).parent.parent.mkdir(parents=True, exist_ok=True)
