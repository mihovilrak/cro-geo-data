CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_municipalities (
    id INT PRIMARY KEY,
    national_code INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    county_code INT NULL,
    updated_at TIMESTAMP NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);