CREATE TABLE IF NOT EXISTS rpj.streets (
    id BIGINT PRIMARY KEY,
    unique_identifier BIGINT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    settlement_code INT NOT NULL REFERENCES settlements(national_code),
    postal_code INT NULL REFERENCES postal_offices(postal_code),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_streets_name ON rpj.streets (name);
CREATE INDEX IF NOT EXISTS idx_streets_settlement_code ON rpj.streets (settlement_code);
CREATE INDEX IF NOT EXISTS idx_streets_postal_code ON rpj.streets (postal_code);
