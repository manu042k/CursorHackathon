"""Process-level Cursor AsyncClient. Architecture §6.3."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from app import settings
from app.store import data_root


@asynccontextmanager
async def cursor_lifespan(app):
    app.state.cursor = None
    if not settings.CURSOR_API_KEY or os.environ.get("PYTEST_CURRENT_TEST"):
        yield
        return
    from cursor_sdk import AsyncClient

    async with await AsyncClient.launch_bridge(workspace=str(data_root())) as client:
        app.state.cursor = client
        yield
        app.state.cursor = None
