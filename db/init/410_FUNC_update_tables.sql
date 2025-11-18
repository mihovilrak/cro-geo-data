CREATE OR REPLACE FUNCTION staging.update_tables()
RETURNS VOID AS $$
BEGIN

    SELECT staging.update_staging();

    ALTER TABLE rpj.municipalities
    DROP CONSTRAINT fk_municipalities_counties;

    ALTER TABLE rpj.settlements
    DROP CONSTRAINT fk_settlements_municipalities;

    ALTER TABLE rpj.streets
    DROP CONSTRAINT fk_streets_settlements;

    ALTER TABLE rpj.streets
    DROP CONSTRAINT fk_streets_postal_offices;

    ALTER TABLE rpj.addresses
    DROP CONSTRAINT fk_addresses_streets;

    ALTER TABLE dkp.cadastral_parcels
    DROP CONSTRAINT fk_cadastral_parcels_cadastral_municipalities;

    ALTER TABLE dkp.buildings
    DROP CONSTRAINT fk_buildings_cadastral_municipalities;

    ALTER TABLE dkp.buildings
    DROP CONSTRAINT fk_buildings_usages;

    CREATE TABLE IF NOT EXISTS rpj.country_new
    (LIKE rpj.country INCLUDING DEFAULTS);

    INSERT INTO rpj.country_new
    (id, national_code, name, updated_at, geom)
    SELECT * FROM staging.u_country;

    TRUNCATE TABLE staging.u_country;

    INSERT INTO journal.j_country
    SELECT * FROM staging.diff('rpj', 'country', 'country_new');

    ALTER TABLE rpj.country
    RENAME TO country_old;

    ALTER TABLE rpj.country_new
    RENAME TO country;

    DROP TABLE rpj.country_old;

    ALTER TABLE rpj.country
    ADD CONSTRAINT pk_country PRIMARY KEY (id);

    VACUUM ANALYZE rpj.country;

    CREATE TABLE IF NOT EXISTS rpj.counties_new
    (LIKE rpj.counties INCLUDING DEFAULTS);

    INSERT INTO rpj.counties_new
    (id, national_code, name, updated_at, geom)
    SELECT * FROM staging.u_counties;

    TRUNCATE TABLE staging.u_counties;

    INSERT INTO journal.j_counties
    SELECT * FROM staging.diff('rpj', 'counties', 'counties_new');

    ALTER TABLE rpj.counties
    RENAME TO counties_old;

    ALTER TABLE rpj.counties_new
    RENAME TO counties;

    DROP TABLE rpj.counties_old;

    CREATE INDEX idx_counties_national_code
    ON rpj.counties (national_code);
        
    CREATE INDEX idx_counties_geom
    ON rpj.counties USING GIST (geom);

    ALTER TABLE rpj.counties
    ADD CONSTRAINT pk_counties PRIMARY KEY (id);
        
    ALTER TABLE rpj.counties
    ADD CONSTRAINT fk_counties_country
    FOREIGN KEY (national_code)
    REFERENCES rpj.country (national_code);

    VACUUM ANALYZE rpj.counties;

    CREATE TABLE IF NOT EXISTS rpj.municipalities_new
    (LIKE rpj.municipalities INCLUDING DEFAULTS);

    INSERT INTO rpj.municipalities_new
    (id, national_code, name, county_code, updated_at, geom)
    SELECT * FROM staging.u_municipalities;

    TRUNCATE TABLE staging.u_municipalities;

    INSERT INTO journal.j_municipalities
    SELECT * FROM staging.diff('rpj', 'municipalities', 'municipalities_new');

    ALTER TABLE rpj.municipalities
    RENAME TO municipalities_old;

    ALTER TABLE rpj.municipalities_new
    RENAME TO municipalities;

    DROP TABLE rpj.municipalities_old;

    CREATE INDEX idx_municipalities_national_code
    ON rpj.municipalities (national_code);
        
    CREATE INDEX idx_municipalities_county_code
    ON rpj.municipalities (county_code);
        
    CREATE INDEX idx_municipalities_geom
    ON rpj.municipalities USING GIST (geom);

    ALTER TABLE rpj.municipalities
    ADD CONSTRAINT pk_municipalities PRIMARY KEY (id);
        
    ALTER TABLE rpj.municipalities
    ADD CONSTRAINT fk_municipalities_counties
    FOREIGN KEY (county_code)
    REFERENCES rpj.counties (national_code);

    VACUUM ANALYZE rpj.municipalities;

    CREATE TABLE IF NOT EXISTS rpj.settlements_new
    (LIKE rpj.settlements INCLUDING DEFAULTS);

    INSERT INTO rpj.settlements_new
    (id, national_code, municipality_code, name, updated_at, geom)
    SELECT * FROM staging.u_settlements;

    TRUNCATE TABLE staging.u_settlements;

    INSERT INTO journal.j_settlements
    SELECT * FROM staging.diff('rpj', 'settlements', 'settlements_new');

    ALTER TABLE rpj.settlements
    RENAME TO settlements_old;

    ALTER TABLE rpj.settlements_new
    RENAME TO settlements;

    DROP TABLE rpj.settlements_old;

    CREATE INDEX idx_settlements_national_code
    ON rpj.settlements (national_code);
        
    CREATE INDEX idx_settlements_municipality_code
    ON rpj.settlements (municipality_code);
        
    CREATE INDEX idx_settlements_name
    ON rpj.settlements (name);
        
    CREATE INDEX idx_settlements_geom
    ON rpj.settlements USING GIST (geom);

    ALTER TABLE rpj.settlements
    ADD CONSTRAINT pk_settlements PRIMARY KEY (id);

    ALTER TABLE rpj.settlements
    ADD CONSTRAINT fk_settlements_municipalities
    FOREIGN KEY (municipality_code)
    REFERENCES rpj.municipalities (national_code);

    VACUUM ANALYZE rpj.settlements;

    CREATE TABLE IF NOT EXISTS rpj.streets_new
    (LIKE rpj.streets INCLUDING DEFAULTS);

    INSERT INTO rpj.streets_new
    (id, name, settlement_code, alternate_code, updated_at)
    SELECT * FROM staging.u_streets;

    TRUNCATE TABLE staging.u_streets;

    INSERT INTO journal.j_streets
    SELECT * FROM staging.diff('rpj', 'streets', 'streets_new');

    ALTER TABLE rpj.streets
    RENAME TO streets_old;

    ALTER TABLE rpj.streets_new
    RENAME TO streets;

    CREATE INDEX idx_streets_settlement_code
    ON rpj.streets (settlement_code);

    CREATE INDEX idx_streets_name
    ON rpj.streets (name);

    DROP TABLE rpj.streets_old;

    ALTER TABLE rpj.streets
    ADD CONSTRAINT pk_streets PRIMARY KEY (id);

    ALTER TABLE rpj.streets
    ADD CONSTRAINT fk_streets_settlements
    FOREIGN KEY (settlement_code)
    REFERENCES rpj.settlements (national_code);

    VACUUM ANALYZE rpj.streets;

    CREATE TABLE IF NOT EXISTS rpj.addresses_new
    (LIKE rpj.addresses INCLUDING DEFAULTS);

    INSERT INTO rpj.addresses_new
    (id, street_id, house_number, updated_at, geom)
    SELECT id, street_id, house_number, updated_at, geom
    FROM staging.u_addresses;

    TRUNCATE TABLE staging.u_addresses;

    INSERT INTO journal.j_addresses
    SELECT * FROM diff('rpj', 'addresses', 'addresses_new');

    ALTER TABLE rpj.addresses
    RENAME TO addresses_old;

    ALTER TABLE rpj.addresses_new
    RENAME TO addresses;

    DROP TABLE rpj.addresses_old;

    CREATE INDEX idx_addresses_street_id
    ON rpj.addresses (street_id);
        
    CREATE INDEX idx_addresses_geom
    ON rpj.addresses USING GIST (geom);

    ALTER TABLE rpj.addresses
    ADD CONSTRAINT pk_addresses PRIMARY KEY (id);

    ALTER TABLE rpj.addresses
    ADD CONSTRAINT fk_addresses_streets 
    FOREIGN KEY (street_id)
    REFERENCES rpj.streets (id);

    VACUUM ANALYZE rpj.addresses;

    CREATE TABLE IF NOT EXISTS dkp.cadastral_municipalities_new
    (LIKE dkp.cadastral_municipalities INCLUDING DEFAULTS);

    INSERT INTO dkp.cadastral_municipalities_new
    (id, national_code, name, harmonization_status, updated_at, geom)
    SELECT * FROM staging.u_cadastral_municipalities;

    TRUNCATE TABLE staging.u_cadastral_municipalities;

    INSERT INTO journal.j_cadastral_municipalities
    SELECT * FROM staging.diff(
        'dkp',
        'cadastral_municipalities',
        'cadastral_municipalities_new'
    );

    ALTER TABLE dkp.cadastral_municipalities
    RENAME TO cadastral_municipalities_old;

    ALTER TABLE dkp.cadastral_municipalities_new
    RENAME TO cadastral_municipalities;

    DROP TABLE dkp.cadastral_municipalities_old;

    CREATE INDEX idx_cadastral_municipalities_national_code
    ON dkp.cadastral_municipalities (national_code);
        
    CREATE INDEX idx_cadastral_municipalities_geom 
    ON dkp.cadastral_municipalities USING GIST (geom);
        
    ALTER TABLE dkp.cadastral_municipalities 
    ADD CONSTRAINT pk_cadastral_municipalities PRIMARY KEY (id);
        
    VACUUM ANALYZE dkp.cadastral_municipalities;

    CREATE TABLE IF NOT EXISTS dkp.cadastral_parcels_new
    (LIKE dkp.cadastral_parcels INCLUDING DEFAULTS);

    INSERT INTO dkp.cadastral_parcels_new
    (id, parcel_code, cadastral_municipality_code,
    graphical_area, updated_at, geom)
    SELECT * FROM staging.u_cadastral_parcels;

    TRUNCATE TABLE staging.u_cadastral_parcels;

    INSERT INTO journal.j_cadastral_parcels
    SELECT * FROM staging.diff('dkp', 'cadastral_parcels', 'cadastral_parcels_new');

    ALTER TABLE dkp.cadastral_parcels
    RENAME TO cadastral_parcels_old;

    ALTER TABLE dkp.cadastral_parcels_new
    RENAME TO cadastral_parcels;

    DROP TABLE dkp.cadastral_parcels_old;

    CREATE INDEX idx_cadastral_parcels_cadastral_municipality_code
    ON dkp.cadastral_parcels (cadastral_municipality_code);

    CREATE INDEX idx_cadastral_parcels_parcel_code
    ON dkp.cadastral_parcels (parcel_code);
        
    CREATE INDEX idx_cadastral_parcels_geom
    ON dkp.cadastral_parcels USING GIST (geom);

    ALTER TABLE dkp.cadastral_parcels
    ADD CONSTRAINT pk_cadastral_parcels PRIMARY KEY (id);

    ALTER TABLE dkp.cadastral_parcels
    ADD CONSTRAINT fk_cadastral_parcels_cadastral_municipalities
    FOREIGN KEY (cadastral_municipality_code)
    REFERENCES dkp.cadastral_municipalities (national_code);

    VACUUM ANALYZE dkp.cadastral_parcels;
        
    CREATE TABLE IF NOT EXISTS dkp.buildings_new
    (LIKE dkp.buildings INCLUDING DEFAULTS);

    INSERT INTO dkp.buildings_new
    (id, building_number, usage_code,
    cadastral_municipality_code, updated_at, geom)
    SELECT * FROM staging.u_buildings;

    TRUNCATE TABLE staging.u_buildings;

    INSERT INTO journal.j_buildings
    SELECT * FROM staging.diff('dkp', 'buildings', 'buildings_new');

    ALTER TABLE dkp.buildings
    RENAME TO buildings_old;

    ALTER TABLE dkp.buildings_new
    RENAME TO buildings;

    DROP TABLE dkp.buildings_old;

    CREATE INDEX idx_buildings_cadastral_municipality_code
    ON dkp.buildings (cadastral_municipality_code);

    CREATE INDEX idx_buildings_building_number
    ON dkp.buildings (building_number);

    CREATE INDEX idx_buildings_usage_code
    ON dkp.buildings (usage_code);

    CREATE INDEX idx_buildings_geom
    ON dkp.buildings USING GIST (geom);

    ALTER TABLE dkp.buildings
    ADD CONSTRAINT pk_buildings PRIMARY KEY (id);

    ALTER TABLE dkp.buildings
    ADD CONSTRAINT fk_buildings_cadastral_municipalities
    FOREIGN KEY (cadastral_municipality_code)
    REFERENCES dkp.cadastral_municipalities (national_code);

    VACUUM ANALYZE dkp.buildings;

END;
$$ LANGUAGE plpgsql;
