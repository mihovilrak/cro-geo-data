CREATE UNLOGGED TABLE IF NOT EXISTS staging.u_streets (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    settlement_code INT NOT NULL,
    alternate_code INT NOT NULL,
    updated_at TIMESTAMP NOT NULL
);