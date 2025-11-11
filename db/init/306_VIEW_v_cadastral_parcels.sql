CREATE OR REPLACE VIEW gs.v_cadastral_parcels AS
    SELECT cp.id,
        cp.parcel_code,
        cp.cadastral_municipality_code,
        cm.name AS cadastral_municipality_name,
        cp.graphical_area,
        cp.geom
    FROM dkp.cadastral_parcels cp
    LEFT JOIN dkp.cadastral_municipalities cm ON cp.cadastral_municipality_code = cm.national_code;
