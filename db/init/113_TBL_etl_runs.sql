CREATE TABLE IF NOT EXISTS journal.etl_runs (
    id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    error_message TEXT,
    downloads_performed BOOLEAN NOT NULL DEFAULT false,
    geoserver_published BOOLEAN NOT NULL DEFAULT false,
    records_inserted INTEGER,
    records_deleted INTEGER,
    records_updated INTEGER,
    duration_seconds INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_etl_runs_started_at
ON journal.etl_runs (started_at DESC);

CREATE INDEX IF NOT EXISTS idx_etl_runs_status
ON journal.etl_runs (status);
