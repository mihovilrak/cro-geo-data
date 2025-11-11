CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_addresses (
    id BIGINT PRIMARY KEY,
    alternate_address VARCHAR(255) NULL,
    street_id BIGINT NULL,
    street_name VARCHAR(255) NULL,
    house_number VARCHAR(10) NULL,
    settlement_id INT NULL,
    settlement_name VARCHAR(255) NULL,
    zip INT NULL,
    updated_at TIMESTAMP NOT NULL,
    geom GEOMETRY(POINT, 3765) NULL
);