CREATE OR REPLACE MATERIALIZED VIEW gs.mv_streets AS
    SELECT s.id,
        s.name,
        s.alternate_code,
        s.settlement_code,
        stl.name AS settlement_name,
        cnt.name AS county_name,
        sg.geom
    FROM rpj.streets s
    JOIN rpj.settlements stl ON s.settlement_code = stl.national_code
    JOIN rpj.counties cnt ON stl.county_code = cnt.national_code
    JOIN gs.v_street_geoms sg ON s.id = sg.street_id;

CREATE INDEX IF NOT EXISTS idx_mv_streets_geom ON gs.mv_streets USING GIST (geom);