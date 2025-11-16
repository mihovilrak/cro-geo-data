CREATE MATERIALIZED VIEW IF NOT EXISTS gs.mv_streets AS
    SELECT s.id,
        s.name,
        s.unique_identifier,
        s.settlement_code,
        stl.name AS settlement_name,
        m.name AS municipality_name,
        cnt.name AS county_name,
        sg.geom
    FROM rpj.streets s
    LEFT JOIN rpj.settlements stl ON s.settlement_code = stl.national_code
    LEFT JOIN rpj.municipalities m ON stl.municipality_code = m.national_code
    LEFT JOIN rpj.counties cnt ON m.county_code = cnt.national_code
    LEFT JOIN gs.v_street_geoms sg ON s.id = sg.street_id;

CREATE INDEX IF NOT EXISTS idx_mv_streets_geom ON gs.mv_streets USING GIST (geom);