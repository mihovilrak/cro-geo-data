CREATE TABLE IF NOT EXISTS municipalities (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    county_id INT NOT NULL REFERENCES counties(id),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_municipalities_geom ON municipalities USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_municipalities_county_id ON municipalities (county_id);