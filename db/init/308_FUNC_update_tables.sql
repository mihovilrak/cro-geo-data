CREATE OR REPLACE FUNCTION staging.update_tables()
RETURNS VOID AS $$
BEGIN;

    SELECT staging.update_staging();

    IF EXISTS (SELECT 1 FROM staging.u_addresses) THEN
        ALTER TABLE rpj.addresses SET UNLOGGED;

        DROP INDEX IF EXISTS idx_addresses_street_id;
        DROP INDEX IF EXISTS idx_addresses_geom;

        DROP CONSTRAINT IF EXISTS fk_addresses_streets;
        DROP CONSTRAINT IF EXISTS pk_addresses;

        DELETE FROM rpj.addresses
        WHERE id IN (SELECT id FROM staging.u_addresses);

        INSERT INTO rpj.addresses 
        (id, street_id, house_number, updated_at, geom)
        SELECT id, street_id, house_number, updated_at, geom
        FROM staging.u_addresses;

        TRUNCATE TABLE staging.u_addresses;

        CREATE INDEX idx_addresses_street_id ON rpj.addresses (street_id);
        CREATE INDEX idx_addresses_geom ON rpj.addresses USING GIST (geom);

        ALTER TABLE rpj.addresses ADD CONSTRAINT pk_addresses PRIMARY KEY (id);

        ALTER TABLE rpj.addresses ADD CONSTRAINT fk_addresses_streets 
        FOREIGN KEY (street_id) REFERENCES rpj.streets (id);
        ALTER TABLE rpj.addresses SET LOGGED;

        VACUUM ANALYZE rpj.addresses;

    END IF;

    IF EXISTS (SELECT 1 FROM staging.u_streets) THEN
        ALTER TABLE rpj.streets SET UNLOGGED;

        DROP INDEX IF EXISTS idx_streets_settlement_code;
        DROP INDEX IF EXISTS idx_streets_name;

        DROP CONSTRAINT IF EXISTS fk_streets_settlements;
        DROP CONSTRAINT IF EXISTS pk_streets;

        DELETE FROM rpj.streets
        WHERE id IN (SELECT id FROM staging.u_streets);

        INSERT INTO rpj.streets
        (id, name, settlement_code, alternate_code, updated_at)
        SELECT * FROM staging.u_streets;

        TRUNCATE TABLE staging.u_streets;

        CREATE INDEX idx_streets_settlement_code ON rpj.streets (settlement_code);
        CREATE INDEX idx_streets_name ON rpj.streets (name);

        ALTER TABLE rpj.streets ADD CONSTRAINT pk_streets PRIMARY KEY (id);

        ALTER TABLE rpj.streets ADD CONSTRAINT fk_streets_settlements
        FOREIGN KEY (settlement_code) REFERENCES rpj.settlements (national_code);
        ALTER TABLE rpj.streets SET LOGGED;

        VACUUM ANALYZE rpj.streets;

    END IF;

    IF EXISTS (SELECT 1 FROM staging.u_settlements) THEN
        ALTER TABLE rpj.settlements SET UNLOGGED;

        DROP INDEX IF EXISTS idx_settlements_national_code;
        DROP INDEX IF EXISTS idx_settlements_municipality_code;
        DROP INDEX IF EXISTS idx_settlements_name;
        DROP INDEX IF EXISTS idx_settlements_geom;

        DROP CONSTRAINT IF EXISTS fk_settlements_municipalities;
        DROP CONSTRAINT IF EXISTS pk_settlements;

        DELETE FROM rpj.settlements
        WHERE id IN (SELECT id FROM staging.u_settlements);

        INSERT INTO rpj.settlements
        (id, national_code, municipality_code, name, updated_at, geom)
        SELECT * FROM staging.u_settlements;

        TRUNCATE TABLE staging.u_settlements;

        CREATE INDEX idx_settlements_national_code ON rpj.settlements (national_code);
        CREATE INDEX idx_settlements_municipality_code ON rpj.settlements (municipality_code);
        CREATE INDEX idx_settlements_name ON rpj.settlements (name);
        CREATE INDEX idx_settlements_geom ON rpj.settlements USING GIST (geom);

        ALTER TABLE rpj.settlements ADD CONSTRAINT pk_settlements PRIMARY KEY (id);

        ALTER TABLE rpj.settlements ADD CONSTRAINT fk_settlements_municipalities
        FOREIGN KEY (municipality_code) REFERENCES rpj.municipalities (national_code);
        ALTER TABLE rpj.settlements SET LOGGED;

        VACUUM ANALYZE rpj.settlements;

    END IF;

    IF EXISTS (SELECT 1 FROM staging.u_municipalities) THEN

        ALTER TABLE rpj.municipalities SET UNLOGGED;

        DROP INDEX IF EXISTS idx_municipalities_national_code;
        DROP INDEX IF EXISTS idx_municipalities_county_code;
        DROP INDEX IF EXISTS idx_municipalities_geom;

        DROP CONSTRAINT IF EXISTS fk_municipalities_counties;
        DROP CONSTRAINT IF EXISTS pk_municipalities;

        DELETE FROM rpj.municipalities
        WHERE id IN (SELECT id FROM staging.u_municipalities);

        INSERT INTO rpj.municipalities
        (id, national_code, name, county_code, updated_at, geom)
        SELECT * FROM staging.u_municipalities;

        TRUNCATE TABLE staging.u_municipalities;

        CREATE INDEX idx_municipalities_national_code ON rpj.municipalities (national_code);
        CREATE INDEX idx_municipalities_county_code ON rpj.municipalities (county_code);
        CREATE INDEX idx_municipalities_geom ON rpj.municipalities USING GIST (geom);

        ALTER TABLE rpj.municipalities ADD CONSTRAINT pk_municipalities PRIMARY KEY (id);
        ALTER TABLE rpj.municipalities ADD CONSTRAINT fk_municipalities_counties
        FOREIGN KEY (county_code) REFERENCES rpj.counties (national_code);
        ALTER TABLE rpj.municipalities SET LOGGED;

        VACUUM ANALYZE rpj.municipalities;

    END IF;

    IF EXISTS (SELECT 1 FROM staging.u_counties) THEN

        ALTER TABLE rpj.counties SET UNLOGGED;

        DROP INDEX IF EXISTS idx_counties_national_code;
        DROP INDEX IF EXISTS idx_counties_geom;

        DROP CONSTRAINT IF EXISTS fk_counties_country;
        DROP CONSTRAINT IF EXISTS pk_counties;

        DELETE FROM rpj.counties
        WHERE id IN (SELECT id FROM staging.u_counties);

        INSERT INTO rpj.counties
        (id, national_code, name, updated_at, geom)
        SELECT * FROM staging.u_counties;

        TRUNCATE TABLE staging.u_counties;

        CREATE INDEX idx_counties_national_code ON rpj.counties (national_code);
        CREATE INDEX idx_counties_geom ON rpj.counties USING GIST (geom);

        ALTER TABLE rpj.counties ADD CONSTRAINT pk_counties PRIMARY KEY (id);
        ALTER TABLE rpj.counties ADD CONSTRAINT fk_counties_country
        FOREIGN KEY (national_code) REFERENCES rpj.country (national_code);
        ALTER TABLE rpj.counties SET LOGGED;

        VACUUM ANALYZE rpj.counties;

    END IF;

    IF EXISTS (SELECT 1 FROM staging.u_country) THEN
        ALTER TABLE rpj.country SET UNLOGGED;

        DROP CONSTRAINT IF EXISTS pk_country;

        DELETE FROM rpj.country;

        INSERT INTO rpj.country
        (id, national_code, name, updated_at, geom)
        SELECT * FROM staging.u_country;

        TRUNCATE TABLE staging.u_country;

        ALTER TABLE rpj.country ADD CONSTRAINT pk_country PRIMARY KEY (id);
        ALTER TABLE rpj.country SET LOGGED;

        VACUUM ANALYZE rpj.country;

    END IF;

    IF EXISTS (SELECT 1 FROM staging.u_cadastral_municipalities) THEN
        ALTER TABLE dkp.cadastral_municipalities SET UNLOGGED;
        
        DROP INDEX IF EXISTS idx_cadastral_municipalities_national_code;
        DROP INDEX IF EXISTS idx_cadastral_municipalities_geom;
        
        DROP CONSTRAINT IF EXISTS pk_cadastral_municipalities;
        
        DELETE FROM dkp.cadastral_municipalities
        WHERE id IN (SELECT id FROM staging.u_cadastral_municipalities);
        
        INSERT INTO dkp.cadastral_municipalities
        (id, national_code, name, harmonization_status, updated_at, geom)
        SELECT * FROM staging.u_cadastral_municipalities;

        TRUNCATE TABLE staging.u_cadastral_municipalities;

        CREATE INDEX idx_cadastral_municipalities_national_code ON dkp.cadastral_municipalities (national_code);
        CREATE INDEX idx_cadastral_municipalities_geom ON dkp.cadastral_municipalities USING GIST (geom);
        
        ALTER TABLE dkp.cadastral_municipalities ADD CONSTRAINT pk_cadastral_municipalities PRIMARY KEY (id);
        ALTER TABLE dkp.cadastral_municipalities SET LOGGED;
        
        VACUUM ANALYZE dkp.cadastral_municipalities;
        
    END IF;

    IF EXISTS (SELECT 1 FROM staging.u_cadastral_parcels) THEN
        ALTER TABLE dkp.cadastral_parcels SET UNLOGGED;
        
        DROP INDEX IF EXISTS idx_cadastral_parcels_cadastral_municipality_code;
        DROP INDEX IF EXISTS idx_cadastral_parcels_parcel_code;
        DROP INDEX IF EXISTS idx_cadastral_parcels_geom;
        
        DROP CONSTRAINT IF EXISTS fk_cadastral_parcels_cadastral_municipalities;
        DROP CONSTRAINT IF EXISTS pk_cadastral_parcels;
        
        DELETE FROM dkp.cadastral_parcels
        WHERE id IN (SELECT id FROM staging.u_cadastral_parcels);
        
        INSERT INTO dkp.cadastral_parcels
        (id, parcel_code, cadastral_municipality_code, graphical_area, updated_at, geom)
        SELECT * FROM staging.u_cadastral_parcels;

        TRUNCATE TABLE staging.u_cadastral_parcels;

        CREATE INDEX idx_cadastral_parcels_cadastral_municipality_code ON dkp.cadastral_parcels (cadastral_municipality_code);
        CREATE INDEX idx_cadastral_parcels_parcel_code ON dkp.cadastral_parcels (parcel_code);
        CREATE INDEX idx_cadastral_parcels_geom ON dkp.cadastral_parcels USING GIST (geom);
        
        ALTER TABLE dkp.cadastral_parcels ADD CONSTRAINT pk_cadastral_parcels PRIMARY KEY (id);
        ALTER TABLE dkp.cadastral_parcels ADD CONSTRAINT fk_cadastral_parcels_cadastral_municipalities
        FOREIGN KEY (cadastral_municipality_code) REFERENCES dkp.cadastral_municipalities (national_code);
        ALTER TABLE dkp.cadastral_parcels SET LOGGED;

        VACUUM ANALYZE dkp.cadastral_parcels;

    END IF;
    IF EXISTS (SELECT 1 FROM staging.u_buildings) THEN
        ALTER TABLE dkp.buildings SET UNLOGGED;
        
        DROP INDEX IF EXISTS idx_buildings_cadastral_municipality_code;
        DROP INDEX IF EXISTS idx_buildings_building_number;
        DROP INDEX IF EXISTS idx_buildings_usage_code;
        DROP INDEX IF EXISTS idx_buildings_geom;
        
        DROP CONSTRAINT IF EXISTS fk_buildings_cadastral_municipalities;
        DROP CONSTRAINT IF EXISTS fk_buildings_usages;
        DROP CONSTRAINT IF EXISTS pk_buildings;
        
        DELETE FROM dkp.buildings
        WHERE id IN (SELECT id FROM staging.u_buildings);
        
        INSERT INTO dkp.buildings
        (id, building_number, usage_code, cadastral_municipality_code, updated_at, geom)
        SELECT * FROM staging.u_buildings;
        
        TRUNCATE TABLE staging.u_buildings;

        CREATE INDEX idx_buildings_cadastral_municipality_code ON dkp.buildings (cadastral_municipality_code);
        CREATE INDEX idx_buildings_building_number ON dkp.buildings (building_number);
        CREATE INDEX idx_buildings_usage_code ON dkp.buildings (usage_code);
        CREATE INDEX idx_buildings_geom ON dkp.buildings USING GIST (geom);
        
        ALTER TABLE dkp.buildings ADD CONSTRAINT pk_buildings PRIMARY KEY (id);
        ALTER TABLE dkp.buildings ADD CONSTRAINT fk_buildings_cadastral_municipalities
        FOREIGN KEY (cadastral_municipality_code) REFERENCES dkp.cadastral_municipalities (national_code);
        ALTER TABLE dkp.buildings ADD CONSTRAINT fk_buildings_usages
        FOREIGN KEY (usage_code) REFERENCES dkp.usages (code);
        ALTER TABLE dkp.buildings SET LOGGED;
        
        VACUUM ANALYZE dkp.buildings;
        
    END IF;
END;
$$ LANGUAGE plpgsql;
