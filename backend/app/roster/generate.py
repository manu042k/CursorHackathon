from __future__ import annotations

from app.contracts import CreateExperimentRequest, Roster
from app.roster.fixed_grok_bot import build_roster


def propose_roster(body: CreateExperimentRequest) -> Roster:
    return build_roster(body.random_seed)
