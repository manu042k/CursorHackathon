from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol

OBSERVE_DECIDE = frozenset({"agent.observed", "agent.decided"})


class Ledger(Protocol):
    def append(
        self,
        experiment_id: str,
        event_type: str,
        *,
        run_id: str | None = None,
        round: int | None = None,
        agent_id: str | None = None,
        payload: dict[str, Any],
    ) -> int: ...


@dataclass
class InMemoryLedger:
    _rows: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def append(
        self,
        experiment_id: str,
        event_type: str,
        *,
        run_id: str | None = None,
        round: int | None = None,
        agent_id: str | None = None,
        payload: dict[str, Any],
    ) -> int:
        if event_type in OBSERVE_DECIDE and not payload:
            raise ValueError("payload required for observe/decide")
        rows = self._rows.setdefault(experiment_id, [])
        seq = len(rows) + 1
        rows.append(
            {
                "seq": seq,
                "event_type": event_type,
                "run_id": run_id,
                "round": round,
                "agent_id": agent_id,
                "payload": payload,
            }
        )
        return seq

    def events(self, experiment_id: str) -> list[dict[str, Any]]:
        return list(self._rows.get(experiment_id, []))


class PostgresLedger:
    def __init__(self, conn):
        self._conn = conn
        self._ensured: set[str] = set()

    def append(
        self,
        experiment_id: str,
        event_type: str,
        *,
        run_id: str | None = None,
        round: int | None = None,
        agent_id: str | None = None,
        payload: dict[str, Any],
    ) -> int:
        if event_type in OBSERVE_DECIDE and not payload:
            raise ValueError("payload required for observe/decide")
        
        with self._conn.cursor() as cur:
            # Ensure experiment exists (minimal stub to satisfy FK)
            if experiment_id not in self._ensured:
                cur.execute(
                    """
                    INSERT INTO experiments (
                        id, status, product_name, product_description,
                        current_price, market_size, competitor_count, competitor_price,
                        buyer_price_sensitivity, rounds, random_seed,
                        variable_type, variable_delta, applies_from_round, adapter
                    ) VALUES (
                        %s, 'created', '', '', 0, 0, 0, 0, '', 8, 0, '', '', 1, 'fixture'
                    ) ON CONFLICT (id) DO NOTHING
                    """,
                    (experiment_id,)
                )
                self._ensured.add(experiment_id)
            
            # Get next seq for this experiment
            cur.execute(
                "SELECT COALESCE(MAX(seq), 0) + 1 FROM events WHERE experiment_id = %s",
                (experiment_id,)
            )
            seq = cur.fetchone()[0]
            
            # Insert event
            cur.execute(
                """
                INSERT INTO events (experiment_id, seq, event_type, run_id, round, agent_id, payload)
                VALUES (%s, %s, %s::event_type, %s::run_id, %s, %s, %s)
                """,
                (experiment_id, seq, event_type, run_id, round, agent_id, json.dumps(payload))
            )
            self._conn.commit()
            return seq
