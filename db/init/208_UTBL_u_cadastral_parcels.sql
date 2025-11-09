CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_cadastral_parcels (
    id INT PRIMARY KEY,
    parcel_code VARCHAR(255) NOT NULL,
    cadastral_municipality_code INT NOT NULL,
    graphical_area FLOAT NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);