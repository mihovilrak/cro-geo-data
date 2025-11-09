CREATE TABLE IF NOT EXISTS rpj.addresses (
    id INT PRIMARY KEY,
    street_id INT NOT NULL REFERENCES streets(id),
    house_number VARCHAR(10) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geom GEOMETRY(POINT, 3765) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_addresses_geom ON rpj.addresses USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_addresses_street_id ON rpj.addresses (street_id);