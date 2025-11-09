CREATE TABLE IF NOT EXISTS rpj.streets (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    settlement_code INT NOT NULL REFERENCES settlements(national_code),
    alternate_code INT NOT NULL UNIQUE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    extent GEOMETRY(POLYGON, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_streets_extent ON rpj.streets USING GIST (extent);
CREATE INDEX IF NOT EXISTS idx_streets_name ON rpj.streets (name);
CREATE INDEX IF NOT EXISTS idx_streets_settlement_code ON rpj.streets (settlement_code);