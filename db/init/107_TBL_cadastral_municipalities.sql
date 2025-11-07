CREATE TABLE IF NOT EXISTS cadastral_municipalities (
    id INT PRIMARY KEY,
    national_code INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    harmonization_status INT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cadastral_municipalities_geom 
ON cadastral_municipalities USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_cadastral_municipalities_national_code 
ON cadastral_municipalities (national_code);
