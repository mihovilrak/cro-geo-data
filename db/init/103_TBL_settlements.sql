CREATE TABLE IF NOT EXISTS settlements (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    municipality_id INT NOT NULL REFERENCES municipalities(id),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_settlements_geom ON settlements USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_settlements_municipality_id ON settlements (municipality_id);
CREATE INDEX IF NOT EXISTS idx_settlements_name ON settlements (name);