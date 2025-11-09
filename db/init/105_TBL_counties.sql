CREATE TABLE IF NOT EXISTS rpj.counties (
    id INT PRIMARY KEY,
    national_code INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_counties_geom ON rpj.counties USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_counties_national_code ON rpj.counties (national_code);
