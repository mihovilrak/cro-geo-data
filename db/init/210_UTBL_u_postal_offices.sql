CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_postal_offices (
    id INT PRIMARY KEY,
    postal_code INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    geom GEOMETRY(POINT, 3765) NULL
);