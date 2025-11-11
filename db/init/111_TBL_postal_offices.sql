CREATE TABLE IF NOT EXISTS rpj.postal_offices (
    id BIGINT PRIMARY KEY,
    postal_code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_postal_offices_name
ON rpj.postal_offices (name);
