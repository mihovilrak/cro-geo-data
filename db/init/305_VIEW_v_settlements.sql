CREATE OR REPLACE VIEW gs.v_settlements AS
    SELECT s.id,
        s.name,
        s.municipality_code,
        m.name AS municipality_name,
        s.county_code,
        c.name AS county_name,
        s.geom
    FROM rpj.settlements s
    LEFT JOIN rpj.municipalities m ON s.municipality_code = m.national_code
    LEFT JOIN rpj.counties c ON s.county_code = c.national_code;
