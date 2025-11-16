CREATE OR REPLACE FUNCTION staging.initial_insert()
RETURNS VOID AS $$
BEGIN

    SELECT staging.update_staging();

    INSERT INTO rpj.country
    SELECT * FROM staging.u_country;
    
    TRUNCATE TABLE staging.u_country;

    VACUUM ANALYZE rpj.country;

    DROP INDEX IF EXISTS idx_counties_national_code;
    DROP INDEX IF EXISTS idx_counties_geom;

    ALTER TABLE rpj.counties 
    DROP CONSTRAINT pk_counties;

    INSERT INTO rpj.counties
    SELECT * FROM staging.u_counties;
    
    TRUNCATE TABLE staging.u_counties;

    ALTER TABLE rpj.counties
    ADD CONSTRAINT pk_counties PRIMARY KEY (id);
    
    CREATE INDEX idx_counties_national_code
    ON rpj.counties (national_code);

    CREATE INDEX idx_counties_geom 
    ON rpj.counties USING GIST (geom);
    
    VACUUM ANALYZE rpj.counties;

    DROP INDEX IF EXISTS idx_municipalities_national_code;
    DROP INDEX IF EXISTS idx_municipalities_county_code;
    DROP INDEX IF EXISTS idx_municipalities_geom;

    ALTER TABLE rpj.municipalities 
    DROP CONSTRAINT fk_municipalities_counties;

    ALTER TABLE rpj.municipalities 
    DROP CONSTRAINT pk_municipalities;

    INSERT INTO rpj.municipalities
    SELECT * FROM staging.u_municipalities;

    TRUNCATE TABLE staging.u_municipalities;

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

    VACUUM ANALYZE rpj.municipalities;

    DROP INDEX IF EXISTS idx_settlements_national_code;
    DROP INDEX IF EXISTS idx_settlements_municipality_code;
    DROP INDEX IF EXISTS idx_settlements_name;
    DROP INDEX IF EXISTS idx_settlements_geom;

    ALTER TABLE rpj.settlements 
    DROP CONSTRAINT fk_settlements_municipalities;
    
    ALTER TABLE rpj.settlements 
    DROP CONSTRAINT pk_settlements;

    INSERT INTO rpj.settlements
    SELECT * FROM staging.u_settlements;

    TRUNCATE TABLE staging.u_settlements;

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

    VACUUM ANALYZE rpj.settlements;

    DROP INDEX IF EXISTS idx_postal_offices_postal_name;

    ALTER TABLE rpj.postal_offices 
    DROP CONSTRAINT pk_postal_offices;

    INSERT INTO rpj.postal_offices
    SELECT * FROM staging.u_postal_offices;

    TRUNCATE TABLE staging.u_postal_offices;

    ALTER TABLE rpj.postal_offices 
    ADD CONSTRAINT pk_postal_offices PRIMARY KEY (id);

    CREATE INDEX idx_postal_offices_postal_code 
    ON rpj.postal_offices (postal_code);

    DROP INDEX IF EXISTS idx_streets_settlement_code;
    DROP INDEX IF EXISTS idx_streets_name;

    ALTER TABLE rpj.streets 
    DROP CONSTRAINT fk_streets_settlements;

    ALTER TABLE rpj.streets 
    DROP CONSTRAINT pk_streets;

    INSERT INTO rpj.streets
    SELECT * FROM staging.u_streets;

    TRUNCATE TABLE staging.u_streets;

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

    VACUUM ANALYZE rpj.streets;

    DROP INDEX IF EXISTS idx_addresses_street_id;
    DROP INDEX IF EXISTS idx_addresses_geom;
    
    ALTER TABLE rpj.addresses 
    DROP CONSTRAINT fk_addresses_streets;
    
    ALTER TABLE rpj.addresses 
    DROP CONSTRAINT pk_addresses;

    INSERT INTO rpj.addresses
    SELECT id,
        street_id,
        house_number,
        updated_at,
        geom
    FROM staging.u_addresses;

    TRUNCATE TABLE staging.u_addresses;

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

    DROP INDEX IF EXISTS idx_cadastral_municipalities_national_code;
    DROP INDEX IF EXISTS idx_cadastral_municipalities_geom;
    
    ALTER TABLE dkp.cadastral_municipalities 
    DROP CONSTRAINT pk_cadastral_municipalities;
    
    INSERT INTO dkp.cadastral_municipalities
    SELECT * FROM staging.u_cadastral_municipalities;

    TRUNCATE TABLE staging.u_cadastral_municipalities;

    ALTER TABLE dkp.cadastral_municipalities 
    ADD CONSTRAINT pk_cadastral_municipalities PRIMARY KEY (id);

    CREATE INDEX idx_cadastral_municipalities_national_code 
    ON dkp.cadastral_municipalities (national_code);

    CREATE INDEX idx_cadastral_municipalities_geom 
    ON dkp.cadastral_municipalities USING GIST (geom);

    VACUUM ANALYZE dkp.cadastral_municipalities;

    DROP INDEX IF EXISTS idx_cadastral_parcels_cadastral_municipality_code;
    DROP INDEX IF EXISTS idx_cadastral_parcels_parcel_code;
    DROP INDEX IF EXISTS idx_cadastral_parcels_geom;
    
    ALTER TABLE dkp.cadastral_parcels 
    DROP CONSTRAINT fk_cadastral_parcels_cadastral_municipalities;
    
    ALTER TABLE dkp.cadastral_parcels 
    DROP CONSTRAINT pk_cadastral_parcels;
    
    INSERT INTO dkp.cadastral_parcels
    SELECT * FROM staging.u_cadastral_parcels;

    TRUNCATE TABLE staging.u_cadastral_parcels;

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

    VACUUM ANALYZE dkp.cadastral_parcels;

    DROP INDEX IF EXISTS idx_buildings_cadastral_municipality_code;
    DROP INDEX IF EXISTS idx_buildings_building_number;
    DROP INDEX IF EXISTS idx_buildings_usage_code;
    DROP INDEX IF EXISTS idx_buildings_geom;

    ALTER TABLE dkp.buildings 
    DROP CONSTRAINT fk_buildings_cadastral_municipalities;
    
    ALTER TABLE dkp.buildings 
    DROP CONSTRAINT pk_buildings;

    INSERT INTO dkp.buildings
    SELECT * FROM staging.u_buildings;

    TRUNCATE TABLE staging.u_buildings;

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

    VACUUM ANALYZE dkp.buildings;

END;
$$ LANGUAGE plpgsql;
