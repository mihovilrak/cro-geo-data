CREATE TABLE IF NOT EXISTS rpj.settlements (
    id INT PRIMARY KEY,
    national_code INT NOT NULL UNIQUE,
    municipality_code INT NOT NULL REFERENCES municipalities(national_code),
    name VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_settlements_geom ON rpj.settlements USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_settlements_municipality_code ON rpj.settlements (municipality_code);
CREATE INDEX IF NOT EXISTS idx_settlements_name ON rpj.settlements (name);