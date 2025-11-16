CREATE TABLE IF NOT EXISTS dkp.cadastral_municipalities (
    id INT PRIMARY KEY,
    national_code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    harmonization_status INT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cadastral_municipalities_geom 
ON dkp.cadastral_municipalities USING GIST (geom);

