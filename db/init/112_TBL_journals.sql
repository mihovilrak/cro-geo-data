CREATE TABLE IF NOT EXISTS journal.j_country (
    id BIGSERIAL PRIMARY KEY,
    inserted INTEGER NOT NULL,
    deleted INTEGER NOT NULL,
    updated INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_j_country_created_at
ON journal.j_country (created_at);

CREATE TABLE IF NOT EXISTS journal.j_counties
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_municipalities
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_settlements
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_postal_offices
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_streets
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_addresses
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_cadastral_municipalities
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_cadastral_parcels
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_buildings
(LIKE journal.j_country INCLUDING ALL);

CREATE TABLE IF NOT EXISTS journal.j_usages
(LIKE journal.j_country INCLUDING ALL);
