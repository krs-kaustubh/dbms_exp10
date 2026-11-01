"""Database settings for SAMs.

Values come from environment variables or from a local `.env` file
(created by `python setup_db.py`, never committed to git).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def _load_env_file():
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
# Not "societydb": that name is used by the Exp-3/Exp-4 lab scripts.
DB_NAME = os.getenv("DB_NAME", "sams_db")
SECRET_KEY = os.getenv("SECRET_KEY", "sams-lab-secret-key")
