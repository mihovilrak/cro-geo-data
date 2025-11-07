CREATE TABLE IF NOT EXISTS buildings (
    id INT PRIMARY KEY,
    building_number INT NOT NULL,
    usage_code INT NOT NULL REFERENCES usages(code),
    cadastral_municipality_code INT NOT NULL REFERENCES cadastral_municipalities(national_code),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(POLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_buildings_geom ON buildings USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_buildings_cadastral_municipality_code 
ON buildings (cadastral_municipality_code);
CREATE INDEX IF NOT EXISTS idx_buildings_building_number 
ON buildings (building_number);
CREATE INDEX IF NOT EXISTS idx_buildings_usage_code 
ON buildings (usage_code);
