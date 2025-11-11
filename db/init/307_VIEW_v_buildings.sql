CREATE OR REPLACE VIEW gs.v_buildings AS
    SELECT b.id,
        b.building_number,
        b.usage_code,
        u.name AS usage,
        b.cadastral_municipality_code,
        cm.name AS cadastral_municipality_name,
        b.geom
    FROM dkp.buildings b
    LEFT JOIN dkp.cadastral_municipalities cm ON b.cadastral_municipality_code = cm.national_code
    LEFT JOIN dkp.usages u ON b.usage_code = u.code;