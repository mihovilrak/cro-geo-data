CREATE TABLE IF NOT EXISTS rpj.municipalities (
    id INT PRIMARY KEY,
    national_code INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    county_code INT NOT NULL REFERENCES counties(national_code),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_municipalities_geom ON rpj.municipalities USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_municipalities_county_code ON rpj.municipalities (county_code);
CREATE INDEX IF NOT EXISTS idx_municipalities_national_code ON rpj.municipalities (national_code);