CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_cadastral_municipalities (
    id INT PRIMARY KEY,
    national_code INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    harmonization_status INT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);