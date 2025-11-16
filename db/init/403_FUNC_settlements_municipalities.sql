CREATE OR REPLACE FUNCTION staging.settlements_municipalities()
RETURNS VOID AS $$
BEGIN

    CREATE INDEX IF NOT EXISTS idx_u_settlements_geom 
    ON staging.u_settlements USING GIST (geom);

    CREATE INDEX IF NOT EXISTS idx_u_municipalities_geom 
    ON staging.u_municipalities USING GIST (geom);

    WITH cte AS (
    SELECT s.id,
           m.id AS municipality_id
    FROM staging.u_settlements s
    LEFT JOIN staging.u_municipalities m
      ON m.geom && s.geom
     AND ST_Contains(m.geom, s.geom)
    )
    UPDATE staging.u_settlements s
    SET municipality_id = cte.municipality_id
    FROM cte
    WHERE s.id = cte.id;
END;
$$ LANGUAGE plpgsql;