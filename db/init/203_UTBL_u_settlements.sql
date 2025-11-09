CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_settlements (
    id INT PRIMARY KEY,
    national_code INT NOT NULL,
    municipality_code INT NULL,
    name VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 3765) NOT NULL
);