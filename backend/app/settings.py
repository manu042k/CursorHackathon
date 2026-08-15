"""Env settings. Never commit CURSOR_API_KEY or DATABASE_URL."""

from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv() -> None:
    path = Path(__file__).resolve().parent.parent / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

CURSOR_API_KEY = os.environ.get("CURSOR_API_KEY", "")
CURSOR_MODEL = os.environ.get("CURSOR_MODEL", "composer-2.5")
DEFAULT_ADAPTER = os.environ.get("DEFAULT_ADAPTER", "fixture")
# Supabase session pooler URI (port 5432) with sslmode=require. Empty → in-memory ledger.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
MAX_REASON_CHARS = 400
MAX_HISTORY_CHARS = 800
