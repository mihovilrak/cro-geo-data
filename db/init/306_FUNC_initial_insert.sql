CREATE OR REPLACE FUNCTION staging.initial_insert()
RETURNS VOID AS $$
BEGIN;

    DROP TABLE IF EXISTS rpj.addresses;
    DROP TABLE IF EXISTS rpj.streets;
    DROP TABLE IF EXISTS rpj.settlements;
    DROP TABLE IF EXISTS rpj.municipalities;
    DROP TABLE IF EXISTS rpj.counties;
    DROP TABLE IF EXISTS rpj.country;
    DROP TABLE IF EXISTS dkp.cadastral_municipalities;
    DROP TABLE IF EXISTS dkp.cadastral_parcels;
    DROP TABLE IF EXISTS dkp.buildings;

    CREATE UNLOGGED TABLE rpj.addresses AS
    SELECT id,
        street_id,
        house_number,
        updated_at,
        geom
    FROM staging.u_addresses2;

    ALTER TABLE rpj.addresses 
    ADD CONSTRAINT pk_addresses PRIMARY KEY (id);

    ALTER TABLE rpj.addresses 
    ADD CONSTRAINT fk_addresses_streets 
    FOREIGN KEY (street_id) REFERENCES rpj.streets (id);

    CREATE INDEX idx_addresses_street_id 
    ON rpj.addresses (street_id);

    CREATE INDEX idx_addresses_geom 
    ON rpj.addresses USING GIST (geom);

    ALTER TABLE rpj.addresses LOGGED;

    VACUUM ANALYZE rpj.addresses;

    DROP TABLE IF EXISTS staging.u_addresses2;

    CREATE UNLOGGED TABLE rpj.streets AS
    SELECT id,
        name,
        settlement_code,
        alternate_code,
        updated_at,
        geom
    FROM staging.u_streets;

    ALTER TABLE rpj.streets 
    ADD CONSTRAINT pk_streets PRIMARY KEY (id);
    
    ALTER TABLE rpj.streets 
    ADD CONSTRAINT fk_streets_settlements 
    FOREIGN KEY (settlement_code)
    REFERENCES rpj.settlements (national_code);

    CREATE INDEX idx_streets_settlement_code 
    ON rpj.streets (settlement_code);

    CREATE INDEX idx_streets_name 
    ON rpj.streets (name);

    CREATE INDEX idx_streets_geom 
    ON rpj.streets USING GIST (geom);

    ALTER TABLE rpj.streets LOGGED;

    VACUUM ANALYZE rpj.streets;

    TRUNCATE TABLE IF EXISTS staging.u_streets;

    CREATE UNLOGGED TABLE rpj.settlements AS
    SELECT id,
        national_code,
        municipality_code,
        name,
        updated_at,
        geom
    FROM staging.u_settlements;

    ALTER TABLE rpj.settlements 
    ADD CONSTRAINT pk_settlements PRIMARY KEY (id);

    ALTER TABLE rpj.settlements 
    ADD CONSTRAINT fk_settlements_municipalities 
    FOREIGN KEY (municipality_code) 
    REFERENCES rpj.municipalities (national_code);

    CREATE INDEX idx_settlements_national_code 
    ON rpj.settlements (national_code);

    CREATE INDEX idx_settlements_municipality_code 
    ON rpj.settlements (municipality_code);

    CREATE INDEX idx_settlements_name 
    ON rpj.settlements (name);

    CREATE INDEX idx_settlements_geom 
    ON rpj.settlements USING GIST (geom);

    ALTER TABLE rpj.settlements LOGGED;

    VACUUM ANALYZE rpj.settlements;

    TRUNCATE TABLE staging.u_settlements;

    CREATE UNLOGGED TABLE rpj.municipalities AS
    SELECT id,
        national_code,
        name,
        county_code,
        updated_at,
        geom
    FROM staging.u_municipalities;

    ALTER TABLE rpj.municipalities 
    ADD CONSTRAINT pk_municipalities PRIMARY KEY (id);

    ALTER TABLE rpj.municipalities 
    ADD CONSTRAINT fk_municipalities_counties 
    FOREIGN KEY (county_code)
    REFERENCES rpj.counties (national_code);

    CREATE INDEX idx_municipalities_national_code 
    ON rpj.municipalities (national_code);

    CREATE INDEX idx_municipalities_county_code 
    ON rpj.municipalities (county_code);

    CREATE INDEX idx_municipalities_geom 
    ON rpj.municipalities USING GIST (geom);

    ALTER TABLE rpj.municipalities LOGGED;

    VACUUM ANALYZE rpj.municipalities;

    TRUNCATE TABLE staging.u_municipalities;

    CREATE UNLOGGED TABLE rpj.counties AS
    SELECT id,
        national_code,
        name,
        updated_at,
        geom
    FROM staging.u_counties;
    
    ALTER TABLE rpj.counties 
    ADD CONSTRAINT pk_counties PRIMARY KEY (id);
    
    CREATE INDEX idx_counties_national_code
    ON rpj.counties (national_code);

    CREATE INDEX idx_counties_geom 
    ON rpj.counties USING GIST (geom);
    
    ALTER TABLE rpj.counties LOGGED;
    
    VACUUM ANALYZE rpj.counties;
    
    TRUNCATE TABLE staging.u_counties;

    CREATE UNLOGGED TABLE rpj.country AS
    SELECT id,
        national_code,
        name,
        updated_at,
        geom
    FROM staging.u_country;
    
    ALTER TABLE rpj.country 
    ADD CONSTRAINT pk_country PRIMARY KEY (id);

    ALTER TABLE rpj.country LOGGED;
    
    VACUUM ANALYZE rpj.country;

    TRUNCATE TABLE staging.u_country;

    CREATE UNLOGGED TABLE dkp.cadastral_municipalities AS
    SELECT id,
        national_code,
        name,
        harmonization_status,
        updated_at,
        geom
    FROM staging.u_cadastral_municipalities;

    ALTER TABLE dkp.cadastral_municipalities 
    ADD CONSTRAINT pk_cadastral_municipalities PRIMARY KEY (id);

    CREATE INDEX idx_cadastral_municipalities_national_code 
    ON dkp.cadastral_municipalities (national_code);

    CREATE INDEX idx_cadastral_municipalities_geom 
    ON dkp.cadastral_municipalities USING GIST (geom);

    ALTER TABLE dkp.cadastral_municipalities LOGGED;

    VACUUM ANALYZE dkp.cadastral_municipalities;

    TRUNCATE TABLE staging.u_cadastral_municipalities;

    CREATE UNLOGGED TABLE dkp.cadastral_parcels AS
    SELECT id,
        parcel_code,
        cadastral_municipality_code,
        graphical_area,
        updated_at,
        geom
    FROM staging.u_cadastral_parcels;

    ALTER TABLE dkp.cadastral_parcels 
    ADD CONSTRAINT pk_cadastral_parcels PRIMARY KEY (id);

    ALTER TABLE dkp.cadastral_parcels 
    ADD CONSTRAINT fk_cadastral_parcels_cadastral_municipalities 
    FOREIGN KEY (cadastral_municipality_code) 
    REFERENCES dkp.cadastral_municipalities (national_code);

    CREATE INDEX idx_cadastral_parcels_cadastral_municipality_code 
    ON dkp.cadastral_parcels (cadastral_municipality_code);

    CREATE INDEX idx_cadastral_parcels_parcel_code 
    ON dkp.cadastral_parcels (parcel_code);

    CREATE INDEX idx_cadastral_parcels_geom 
    ON dkp.cadastral_parcels USING GIST (geom);

    ALTER TABLE dkp.cadastral_parcels LOGGED;

    VACUUM ANALYZE dkp.cadastral_parcels;

    TRUNCATE TABLE staging.u_cadastral_parcels;

    CREATE UNLOGGED TABLE dkp.buildings AS
    SELECT id,
        building_number,
        usage_code,
        cadastral_municipality_code,
        updated_at,
        geom
    FROM staging.u_buildings;

    ALTER TABLE dkp.buildings 
    ADD CONSTRAINT pk_buildings PRIMARY KEY (id);

    ALTER TABLE dkp.buildings 
    ADD CONSTRAINT fk_buildings_cadastral_municipalities 
    FOREIGN KEY (cadastral_municipality_code) 
    REFERENCES dkp.cadastral_municipalities (national_code);

    CREATE INDEX idx_buildings_cadastral_municipality_code 
    ON dkp.buildings (cadastral_municipality_code);

    CREATE INDEX idx_buildings_building_number 
    ON dkp.buildings (building_number);

    CREATE INDEX idx_buildings_usage_code 
    ON dkp.buildings (usage_code);

    CREATE INDEX idx_buildings_geom 
    ON dkp.buildings USING GIST (geom);

    ALTER TABLE dkp.buildings LOGGED;

    VACUUM ANALYZE dkp.buildings;

    TRUNCATE TABLE staging.u_buildings;

END;
$$ LANGUAGE plpgsql;
