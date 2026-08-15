-- US-B9: research then confirm. Keep in sync with backend/db/schema.sql comments.
-- Do not rewrite the original enum in 20260815154800_experiment_ledger.sql.

ALTER TYPE experiment_status ADD VALUE IF NOT EXISTS 'researching';
ALTER TYPE experiment_status ADD VALUE IF NOT EXISTS 'roster_ready';
ALTER TYPE event_type ADD VALUE IF NOT EXISTS 'research.started';
ALTER TYPE event_type ADD VALUE IF NOT EXISTS 'research.completed';
