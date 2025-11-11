CREATE TABLE IF NOT EXISTS dkp.buildings (
    id INT PRIMARY KEY,
    building_number INT NOT NULL,
    usage_code INT NOT NULL REFERENCES dkp.usages(code),
    cadastral_municipality_code INT NOT NULL 
        REFERENCES dkp.cadastral_municipalities(national_code),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(POLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_buildings_geom 
ON dkp.buildings USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_buildings_cadastral_municipality_code 
ON dkp.buildings (cadastral_municipality_code);

CREATE INDEX IF NOT EXISTS idx_buildings_building_number 
ON dkp.buildings (building_number);

CREATE INDEX IF NOT EXISTS idx_buildings_usage_code 
ON dkp.buildings (usage_code);
