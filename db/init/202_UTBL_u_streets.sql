CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_streets (
    id BIGINT PRIMARY KEY,
    unique_identifier BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    settlement_code INT NOT NULL,
    postal_code INT NULL,
    updated_at TIMESTAMP NOT NULL
);