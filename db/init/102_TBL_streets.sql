CREATE TABLE IF NOT EXISTS streets (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    settlement_id INT NOT NULL REFERENCES settlements(id),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    extent GEOMETRY(POLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_streets_extent ON streets USING GIST (extent);
CREATE INDEX IF NOT EXISTS idx_streets_name ON streets (name);
CREATE INDEX IF NOT EXISTS idx_streets_settlement_id ON streets (settlement_id);