"""Env settings. Never commit CURSOR_API_KEY."""

from __future__ import annotations

import os

CURSOR_API_KEY = os.environ.get("CURSOR_API_KEY", "")
CURSOR_MODEL = os.environ.get("CURSOR_MODEL", "composer-2.5")
DEFAULT_ADAPTER = os.environ.get("DEFAULT_ADAPTER", "fixture")
