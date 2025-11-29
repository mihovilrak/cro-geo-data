CREATE TABLE IF NOT EXISTS dkp.cadastral_parcels (
    id INT PRIMARY KEY,
    parcel_code VARCHAR(20) NOT NULL,
    cadastral_municipality_code INT NOT NULL
        REFERENCES dkp.cadastral_municipalities(national_code),
    graphical_area NUMERIC(12, 2) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cadastral_parcels_geom
ON dkp.cadastral_parcels USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_cadastral_parcels_cadastral_municipality_code
ON dkp.cadastral_parcels (cadastral_municipality_code);

CREATE INDEX IF NOT EXISTS idx_cadastral_parcels_parcel_code
ON dkp.cadastral_parcels (parcel_code);

CREATE INDEX IF NOT EXISTS idx_cadastral_parcels_municipality_code_parcel_code
ON dkp.cadastral_parcels (cadastral_municipality_code, parcel_code);
