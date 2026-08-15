-- Counterfactual Replay ledger — architecture.md §7.5
-- Apply in Supabase: SQL Editor → Run, or `supabase db push` (see supabase/migrations).
-- FastAPI connects with DATABASE_URL (Postgres URI). Do not use the anon key for this schema.

DO $$ BEGIN
  CREATE TYPE experiment_status AS ENUM (
    'created', 'running_a', 'running_b', 'attributing', 'complete', 'failed'
  );
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE run_id AS ENUM ('A', 'B');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE event_type AS ENUM (
    'experiment.created',
    'roster.frozen',
    'run.started',
    'round.opened',
    'intervention.applied',
    'agent.observed',
    'agent.decided',
    'market.mutated',
    'round.closed',
    'run.completed',
    'alignment.checked',
    'attribution.computed',
    'experiment.completed',
    'experiment.failed'
  );
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS experiments (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  status experiment_status NOT NULL,
  error TEXT,
  product_name TEXT NOT NULL,
  product_description TEXT NOT NULL,
  current_price DOUBLE PRECISION NOT NULL,
  market_size INTEGER NOT NULL,
  competitor_count INTEGER NOT NULL,
  competitor_price DOUBLE PRECISION NOT NULL,
  buyer_price_sensitivity TEXT NOT NULL,
  rounds INTEGER NOT NULL DEFAULT 8,
  random_seed INTEGER NOT NULL,
  variable_type TEXT NOT NULL,
  variable_delta TEXT NOT NULL,
  applies_from_round INTEGER NOT NULL,
  adapter TEXT NOT NULL,
  prompt_hash TEXT,
  roster_hash TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS experiments_user_created_idx
  ON experiments (user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS events (
  id BIGSERIAL PRIMARY KEY,
  experiment_id TEXT NOT NULL REFERENCES experiments (id) ON DELETE CASCADE,
  seq INTEGER NOT NULL CHECK (seq > 0),
  event_type event_type NOT NULL,
  run_id run_id,
  round INTEGER,
  agent_id TEXT,
  payload JSONB NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (experiment_id, seq)
);

CREATE INDEX IF NOT EXISTS events_experiment_type_idx ON events (experiment_id, event_type);
CREATE INDEX IF NOT EXISTS events_experiment_run_round_idx ON events (experiment_id, run_id, round);

-- Application must not UPDATE/DELETE event rows.
REVOKE UPDATE, DELETE ON events FROM PUBLIC;

ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Backend uses the database password (postgres / session pooler), which bypasses RLS.
-- No policies for anon/authenticated → PostgREST cannot read the ledger.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
    REVOKE ALL ON TABLE experiments FROM anon;
    REVOKE ALL ON TABLE events FROM anon;
  END IF;
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
    REVOKE ALL ON TABLE experiments FROM authenticated;
    REVOKE ALL ON TABLE events FROM authenticated;
  END IF;
END $$;
