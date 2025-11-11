CREATE TABLE IF NOT EXISTS postal_offices (
    id INT PRIMARY KEY,
    postal_code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(POINT, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_postal_offices_geom ON postal_offices USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_postal_offices_name ON postal_offices (name);
