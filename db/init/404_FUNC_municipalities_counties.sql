CREATE OR REPLACE FUNCTION staging.municipalities_counties()
RETURNS VOID AS $$
BEGIN

    CREATE INDEX IF NOT EXISTS idx_u_municipalities_geom 
    ON staging.u_municipalities USING GIST (geom);

    CREATE INDEX IF NOT EXISTS idx_u_counties_geom 
    ON staging.u_counties USING GIST (geom);

    WITH cte AS (
    SELECT m.id,
           c.id AS county_id
    FROM staging.u_municipalities m
    LEFT JOIN staging.u_counties c
      ON c.geom && m.geom
     AND ST_Contains(c.geom, m.geom);
    )
    UPDATE staging.u_municipalities m
    SET county_id = cte.county_id
    FROM cte
    WHERE m.id = cte.id;
END;
$$ LANGUAGE plpgsql;
