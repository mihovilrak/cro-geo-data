CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_buildings (
    id INT PRIMARY KEY,
    building_number INT NOT NULL,
    usage_code INT NOT NULL,
    cadastral_municipality_code INT NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);