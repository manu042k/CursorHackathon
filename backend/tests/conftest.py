"""Keep pytest off the live Supabase ledger unless a test opts in."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _empty_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.settings.DATABASE_URL", "")
    monkeypatch.setattr("app.main.settings.DATABASE_URL", "")
