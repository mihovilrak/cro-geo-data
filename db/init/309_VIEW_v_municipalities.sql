CREATE OR REPLACE VIEW gs.v_municipalities AS
    SELECT m.id,
        m.national_code,
        m.name,
        m.county_code,
        c.name AS county_name,
        m.geom
    FROM rpj.municipalities m
    LEFT JOIN rpj.counties c ON m.county_code = c.national_code;